import unittest

import constants
from showdown.battle import Battle
from showdown.battle_bots.helpers import format_decision, get_non_fainted_pokemon_in_reserve, count_fainted_pokemon_in_reserve
from showdown.battle_bots.safest.main import BattleBot as SafestBattleBot
from showdown.engine.objects import Pokemon, Side, State
import json
import pprint
from config import ShowdownConfig
from unittest.mock import patch, MagicMock
import pytest

class TestFormatResponse(unittest.TestCase):
	user_json_one_reserve = """{
		"active": [
			{
				"moves": [
					{
						"move": "Earthquake",
						"id": "earthquake",
						"pp": 16,
						"maxpp": 16,
						"target": "allAdjacentFoes",
						"disabled": false
					},
					{
						"move": "Wood Hammer",
						"id": "woodhammer",
						"pp": 24,
						"maxpp": 24,
						"target": "normal",
						"disabled": false
					},
					{
						"move": "Stone Edge",
						"id": "stoneedge",
						"pp": 8,
						"maxpp": 8,
						"target": "normal",
						"disabled": false
					},
					{
						"move": "Synthesis",
						"id": "synthesis",
						"pp": 8,
						"maxpp": 8,
						"target": "self",
						"disabled": false
					}
				],
				"maybeTrapped": false,
				"canTerastallize": "Ground"
			}
		],
		"side": {
			"name": "cjflexbot2",
			"id": "p2",
			"pokemon": [
				{
					"ident": "p2: Torterra",
					"details": "Torterra, L82, M",
					"condition": "295/295",
					"active": true,
					"stats": {
						"atk": 232,
						"def": 236,
						"spa": 154,
						"spd": 196,
						"spe": 146
					},
					"moves": [
						"earthquake",
						"woodhammer",
						"stoneedge",
						"synthesis"
					],
					"baseAbility": "overgrow",
					"item": "leftovers",
					"pokeball": "pokeball",
					"ability": "overgrow",
					"commanding": false,
					"reviving": false,
					"teraType": "Ground",
					"terastallized": ""
				},
				{
					"ident": "p2: Volcarona",
					"details": "Volcarona, L77, F",
					"condition": "257/257",
					"active": false,
					"stats": {
						"atk": 97,
						"def": 145,
						"spa": 252,
						"spd": 206,
						"spe": 199
					},
					"moves": [
						"gigadrain",
						"fierydance",
						"terablast",
						"quiverdance"
					],
					"baseAbility": "flamebody",
					"item": "heavydutyboots",
					"pokeball": "pokeball",
					"ability": "flamebody",
					"commanding": false,
					"reviving": false,
					"teraType": "Water",
					"terastallized": ""
				}
			]
		},
		"rqid": 3
	}"""

	def setUp(self):
		ShowdownConfig.configure()
		self.opponent_switch_string_weavile = "|switch|p1a: Weavile|Weavile, L92, F|100/100"
		self.mode = "gen9randombattle"
		self.battle_tag = "battle_tag"

		# Set up Safest battlebot
		user_json_one_reserve_parsed = json.loads(self.user_json_one_reserve.strip('\''))
		self.safest_battlebot = SafestBattleBot(self.battle_tag)
		self.safest_battlebot.generation = self.mode[:4]
		self.safest_battlebot.battle_type = constants.RANDOM_BATTLE
		self.safest_battlebot.start_non_team_preview_battle(user_json_one_reserve_parsed, self.opponent_switch_string_weavile)
		# pprint.pprint(self.safest_battlebot.user.active)
		# pprint.pprint(self.safest_battlebot.user.reserve)

	def test_format_decision_switch_valid_pokemon(self):
		decision = "switch volcarona"
		
		# Call the function
		result = format_decision(self.safest_battlebot, decision)

		# Verify the output
		assert result == ["/switch 2", str(self.safest_battlebot.rqid)]

	def test_format_decision_switch_invalid_pokemon(self):
		decision = "switch bulbasaur"
		
		# Expecting a ValueError when trying to switch to a Pokémon not in the reserve
		with pytest.raises(ValueError) as exc_info:
			format_decision(self.safest_battlebot, decision)
		
		assert "Tried to switch to: bulbasaur" in str(exc_info.value)

	def test_format_decision_with_mega_evolution(self):
		self.safest_battlebot.user.active.can_mega_evo = True

		decision = "earthquake"
		
		# Call the function
		result = format_decision(self.safest_battlebot, decision)

		# Verify the output
		assert result == ["/choose move earthquake mega", str(self.safest_battlebot.rqid)]

	def test_format_decision_regular(self):
		# Set up the active Pokémon with no special abilities
		move_name = "Earthquake"
		self.safest_battlebot.user.active.can_mega_evo = False
		self.safest_battlebot.user.active.can_ultra_burst = False
		self.safest_battlebot.user.active.can_dynamax = False
		self.safest_battlebot.user.active.can_terastallize = False

		# Mock the move selection to return a regular move
		mock_move = MagicMock()
		mock_move.can_z = False  # No Z-Move capability
		self.safest_battlebot.user.active.get_move = MagicMock(return_value=mock_move)

		# Call format_decision with the selected move
		decision = move_name
		result = format_decision(self.safest_battlebot, decision)

		# Assert that the decision message is a standard move choice with no additional tags
		expected_message = f"/choose move {move_name}"
		self.assertEqual(result, [expected_message, str(self.safest_battlebot.rqid)])

	def test_format_decision_with_z_move(self):
		# Set up the active Pokemon move as a Z-Move
		move_name = "Earthquake"
		mock_move = MagicMock()
		mock_move.can_z = True
		self.safest_battlebot.user.active.get_move = MagicMock(return_value=mock_move)
		
		# Call format_decision with the selected move
		decision = move_name
		result = format_decision(self.safest_battlebot, decision)
		
		# Assert that the decision message includes Z-Move
		expected_message = f"/choose move {move_name} {constants.ZMOVE}"
		self.assertEqual(result, [expected_message, str(self.safest_battlebot.rqid)])

	def test_format_decision_with_dynamax(self):
		# Set up the active Pokemon to be able to Dynamax
		move_name = "Earthquake"
		self.safest_battlebot.user.active.can_dynamax = True
		
		# Set the reserve Pokemon to fainted to meet the Dynamax condition
		for pokemon in self.safest_battlebot.user.reserve:
			pokemon.hp = 0
		
		# Call format_decision with the selected move
		decision = move_name
		result = format_decision(self.safest_battlebot, decision)
		
		# Assert that the decision message includes Dynamax
		expected_message = f"/choose move {move_name} {constants.DYNAMAX}"
		self.assertEqual(result, [expected_message, str(self.safest_battlebot.rqid)])

	def test_format_decision_with_terastallize(self):
		# Set up the active Pokemon to be able to Terastallize
		move_name = "Earthquake"
		self.safest_battlebot.user.active.can_terastallize = "Ground"
		
		# Set the reserve Pokemon to fainted to meet the Terastallize condition
		for pokemon in self.safest_battlebot.user.reserve:
			pokemon.hp = 0
		
		# Call format_decision with the selected move
		decision = move_name
		result = format_decision(self.safest_battlebot, decision)
		
		# Assert that the decision message includes Terastallize
		expected_message = f"/choose move {move_name} {constants.TERASTALLIZE}"
		self.assertEqual(result, [expected_message, str(self.safest_battlebot.rqid)])

	def test_format_decision_will_not_terastallize_if_not_last_pokemon(self):
		# Set up the active Pokémon to be able to Terastallize
		move_name = "Earthquake"
		self.safest_battlebot.user.active.can_terastallize = "Ground"

		# Ensure there is at least one other non-fainted Pokémon in the reserve
		reserve_pokemon = MagicMock()
		reserve_pokemon.hp = 100  # The Pokémon is still alive
		self.safest_battlebot.user.reserve = [reserve_pokemon]

		# Call format_decision with the selected move
		decision = move_name
		result = format_decision(self.safest_battlebot, decision)

		# Assert that the decision message does not include Terastallize
		expected_message = f"/choose move {move_name}"
		self.assertEqual(result, [expected_message, str(self.safest_battlebot.rqid)])

from showdown.battle import Pokemon as StatePokemon
from collections import defaultdict

class TestGetNonFaintedPokemonInReserve(unittest.TestCase):
	def setUp(self):
		self.maxDiff = None
		self.side = Side(
			Pokemon.from_state_pokemon_dict(StatePokemon("raichu", 73).to_dict()),
			{
				"xatu": Pokemon.from_state_pokemon_dict(StatePokemon("xatu", 81).to_dict()),
				"starmie": Pokemon.from_state_pokemon_dict(StatePokemon("starmie", 81).to_dict()),
				"gyarados": Pokemon.from_state_pokemon_dict(StatePokemon("gyarados", 81).to_dict()),
				"dragonite": Pokemon.from_state_pokemon_dict(StatePokemon("dragonite", 81).to_dict()),
				"hitmonlee": Pokemon.from_state_pokemon_dict(StatePokemon("hitmonlee", 81).to_dict()),
			},
			(0, 0),
			defaultdict(lambda: 0),
			(0, 0)
		)

	def test_all_pokemon_fainted(self):
		for mon in self.side.reserve.values():
			mon.hp = 0
		expected_out = {}
		non_fainted_out = get_non_fainted_pokemon_in_reserve(self.side.reserve)
		self.assertEqual(expected_out, non_fainted_out)

	def test_no_pokemon_fainted(self):
		# All Pokémon have non-zero HP
		expected_out = self.side.reserve
		non_fainted_out = get_non_fainted_pokemon_in_reserve(self.side.reserve)
		self.assertEqual(expected_out, non_fainted_out)

	def test_some_pokemon_fainted(self):
		# Faint some Pokémon
		self.side.reserve["starmie"].hp = 0
		self.side.reserve["gyarados"].hp = 0
		
		expected_out = {
			"xatu": self.side.reserve["xatu"],
			"dragonite": self.side.reserve["dragonite"],
			"hitmonlee": self.side.reserve["hitmonlee"]
		}
		non_fainted_out = get_non_fainted_pokemon_in_reserve(self.side.reserve)
		self.assertEqual(expected_out, non_fainted_out)

	def test_empty_reserve(self):
		# Reserve is empty
		self.side.reserve = {}
		expected_out = {}
		non_fainted_out = get_non_fainted_pokemon_in_reserve(self.side.reserve)
		self.assertEqual(expected_out, non_fainted_out)

	def test_single_non_fainted_pokemon(self):
		# Only one Pokémon in reserve and it's non-fainted
		self.side.reserve = {
			"dragonite": Pokemon.from_state_pokemon_dict(StatePokemon("dragonite", 81).to_dict())
		}
		expected_out = self.side.reserve
		non_fainted_out = get_non_fainted_pokemon_in_reserve(self.side.reserve)
		self.assertEqual(expected_out, non_fainted_out)

	def test_single_fainted_pokemon(self):
		# Only one Pokémon in reserve and it's fainted
		self.side.reserve = {
			"dragonite": Pokemon.from_state_pokemon_dict(StatePokemon("dragonite", 81).to_dict())
		}
		self.side.reserve["dragonite"].hp = 0
		expected_out = {}
		non_fainted_out = get_non_fainted_pokemon_in_reserve(self.side.reserve)
		self.assertEqual(expected_out, non_fainted_out)

import unittest

class TestCountFaintedPokemonInReserve(unittest.TestCase):
	def setUp(self):
		self.reserve = {
			"xatu": StatePokemon("xatu", 81),
			"starmie": StatePokemon("starmie", 81),
			"gyarados": StatePokemon("gyarados", 81),
			"dragonite": StatePokemon("dragonite", 81),
			"hitmonlee": StatePokemon("hitmonlee", 81),
		}

	def test_all_pokemon_fainted(self):
		for mon in self.reserve.values():
			mon.hp = 0
		fainted_count = count_fainted_pokemon_in_reserve(self.reserve)
		self.assertEqual(fainted_count, len(self.reserve))  # Expect all Pokémon to be fainted

	def test_no_pokemon_fainted(self):
		for mon in self.reserve.values():
			mon.hp = 81  # All Pokémon have non-zero HP
		fainted_count = count_fainted_pokemon_in_reserve(self.reserve)
		self.assertEqual(fainted_count, 0)  # Expect no Pokémon to be fainted

	def test_some_pokemon_fainted(self):
		# Faint two Pokémon in the reserve
		self.reserve["starmie"].hp = 0
		self.reserve["gyarados"].hp = 0
		
		fainted_count = count_fainted_pokemon_in_reserve(self.reserve)
		self.assertEqual(fainted_count, 2)  # Expect 2 Pokémon to be fainted

	def test_empty_reserve(self):
		empty_reserve = {}
		fainted_count = count_fainted_pokemon_in_reserve(empty_reserve)
		self.assertEqual(fainted_count, 0)  # Expect 0 fainted Pokémon in an empty reserve

	def test_single_fainted_pokemon(self):
		single_reserve = {
			"dragonite": StatePokemon("dragonite", 81)
		}
		single_reserve["dragonite"].hp = 0
		fainted_count = count_fainted_pokemon_in_reserve(single_reserve)
		self.assertEqual(fainted_count, 1)  # Expect 1 fainted Pokémon

	def test_single_non_fainted_pokemon(self):
		single_reserve = {
			"dragonite": StatePokemon("dragonite", 81)
		}
		fainted_count = count_fainted_pokemon_in_reserve(single_reserve)
		self.assertEqual(fainted_count, 0)  # Expect 0 fainted Pokémon

