import unittest
from collections import defaultdict

import constants
from showdown.battle import Battle
from showdown.battle_bots.llm.main import BattleBot as LLMBattleBot
from showdown.battle_bots.llm.llm_helpers import format_prompt, parse_llm_output
from showdown.battle_bots.safest.main import BattleBot as SafestBattleBot
from showdown.engine.objects import Pokemon, Side, State
import json
import pprint
from config import ShowdownConfig
from unittest.mock import patch, MagicMock

class TestLLMBattleBot(unittest.TestCase):
	user_json = """{
		"active": [
			{
				"moves": [
					{
						"move": "Knock Off",
						"id": "knockoff",
						"pp": 32,
						"maxpp": 32,
						"target": "normal",
						"disabled": false
					},
					{
						"move": "Heavy Slam",
						"id": "heavyslam",
						"pp": 16,
						"maxpp": 16,
						"target": "normal",
						"disabled": false
					},
					{
						"move": "Draco Meteor",
						"id": "dracometeor",
						"pp": 8,
						"maxpp": 8,
						"target": "normal",
						"disabled": false
					},
					{
						"move": "Hydro Pump",
						"id": "hydropump",
						"pp": 8,
						"maxpp": 8,
						"target": "normal",
						"disabled": false
					}
				],
				"maybeTrapped": true,
				"canTerastallize": "Dragon"
			}
		],
		"side": {
			"name": "cjflexbot2",
			"id": "p2",
			"pokemon": [
				{
					"ident": "p2: Goodra",
					"details": "Goodra-Hisui, L82, M",
					"condition": "265/265",
					"active": true,
					"stats": {
						"atk": 211,
						"def": 211,
						"spa": 228,
						"spd": 293,
						"spe": 146
					},
					"moves": [
						"knockoff",
						"heavyslam",
						"dracometeor",
						"hydropump"
					],
					"baseAbility": "sapsipper",
					"item": "assaultvest",
					"pokeball": "pokeball",
					"ability": "sapsipper",
					"commanding": false,
					"reviving": false,
					"teraType": "Dragon",
					"terastallized": ""
				},
				{
					"ident": "p2: Chi-Yu",
					"details": "Chi-Yu, L77",
					"condition": "211/211",
					"active": false,
					"stats": {
						"atk": 128,
						"def": 168,
						"spa": 252,
						"spd": 229,
						"spe": 199
					},
					"moves": [
						"darkpulse",
						"overheat",
						"flamethrower",
						"psychic"
					],
					"baseAbility": "beadsofruin",
					"item": "choicescarf",
					"pokeball": "pokeball",
					"ability": "beadsofruin",
					"commanding": false,
					"reviving": false,
					"teraType": "Fire",
					"terastallized": ""
				},
				{
					"ident": "p2: Whiscash",
					"details": "Whiscash, L88, F",
					"condition": "337/337",
					"active": false,
					"stats": {
						"atk": 188,
						"def": 179,
						"spa": 184,
						"spd": 175,
						"spe": 156
					},
					"moves": [
						"icebeam",
						"stealthrock",
						"earthquake",
						"spikes"
					],
					"baseAbility": "oblivious",
					"item": "leftovers",
					"pokeball": "pokeball",
					"ability": "oblivious",
					"commanding": false,
					"reviving": false,
					"teraType": "Poison",
					"terastallized": ""
				},
				{
					"ident": "p2: Appletun",
					"details": "Appletun, L92, F",
					"condition": "352/352",
					"active": false,
					"stats": {
						"atk": 161,
						"def": 200,
						"spa": 236,
						"spd": 200,
						"spe": 108
					},
					"moves": [
						"dracometeor",
						"recover",
						"leechseed",
						"appleacid"
					],
					"baseAbility": "thickfat",
					"item": "leftovers",
					"pokeball": "pokeball",
					"ability": "thickfat",
					"commanding": false,
					"reviving": false,
					"teraType": "Steel",
					"terastallized": ""
				},
				{
					"ident": "p2: Toxapex",
					"details": "Toxapex, L82, F",
					"condition": "216/216",
					"active": false,
					"stats": {
						"atk": 150,
						"def": 296,
						"spa": 134,
						"spd": 280,
						"spe": 105
					},
					"moves": [
						"toxic",
						"liquidation",
						"haze",
						"recover"
					],
					"baseAbility": "regenerator",
					"item": "rockyhelmet",
					"pokeball": "pokeball",
					"ability": "regenerator",
					"commanding": false,
					"reviving": false,
					"teraType": "Grass",
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
	
	user_json_no_reserve = """{
		"active": [
			{
				"moves": [
					{
						"move": "Knock Off",
						"id": "knockoff",
						"pp": 32,
						"maxpp": 32,
						"target": "normal",
						"disabled": false
					},
					{
						"move": "Heavy Slam",
						"id": "heavyslam",
						"pp": 16,
						"maxpp": 16,
						"target": "normal",
						"disabled": false
					},
					{
						"move": "Draco Meteor",
						"id": "dracometeor",
						"pp": 8,
						"maxpp": 8,
						"target": "normal",
						"disabled": false
					},
					{
						"move": "Hydro Pump",
						"id": "hydropump",
						"pp": 8,
						"maxpp": 8,
						"target": "normal",
						"disabled": false
					}
				],
				"maybeTrapped": true
			}
		],
		"side": {
			"name": "cjflexbot2",
			"id": "p2",
			"pokemon": [
				{
					"ident": "p2: Goodra",
					"details": "Goodra-Hisui, L82, M",
					"condition": "265/265",
					"active": true,
					"stats": {
						"atk": 211,
						"def": 211,
						"spa": 228,
						"spd": 293,
						"spe": 146
					},
					"moves": [
						"knockoff",
						"heavyslam",
						"dracometeor",
						"hydropump"
					],
					"baseAbility": "sapsipper",
					"item": "assaultvest",
					"pokeball": "pokeball",
					"ability": "sapsipper",
					"commanding": false,
					"reviving": false
				}
			]
		},
		"rqid": 3
	}"""

	user_json_no_reserve_no_damaging_moves = """{
		"active": [
			{
				"moves": [
					{
						"move": "Toxic",
						"id": "toxic",
						"pp": 16,
						"maxpp": 16,
						"target": "normal",
						"disabled": false
					},
					{
						"move": "Protect",
						"id": "protect",
						"pp": 16,
						"maxpp": 16,
						"target": "self",
						"disabled": false
					},
					{
						"move": "Thunder Wave",
						"id": "thunderwave",
						"pp": 32,
						"maxpp": 32,
						"target": "normal",
						"disabled": false
					},
					{
						"move": "Substitute",
						"id": "substitute",
						"pp": 16,
						"maxpp": 16,
						"target": "self",
						"disabled": false
					}
				],
				"maybeTrapped": true,
				"canTerastallize": "Dragon"
			}
		],
		"side": {
			"name": "cjflexbot2",
			"id": "p2",
			"pokemon": [
				{
					"ident": "p2: Goodra",
					"details": "Goodra-Hisui, L82, M",
					"condition": "265/265",
					"active": true,
					"stats": {
						"atk": 211,
						"def": 211,
						"spa": 228,
						"spd": 293,
						"spe": 146
					},
					"moves": [
						"toxic",
						"protect",
						"thunderwave",
						"substitute"
					],
					"baseAbility": "sapsipper",
					"item": "assaultvest",
					"pokeball": "pokeball",
					"ability": "sapsipper",
					"commanding": false,
					"reviving": false,
					"teraType": "Dragon",
					"terastallized": ""
				}
			]
		},
		"rqid": 3
	}
	"""

	def setUp(self):
		ShowdownConfig.configure()
		user_json_parsed = json.loads(self.user_json.strip('\''))
		user_json_no_reserve_parsed = json.loads(self.user_json_no_reserve.strip('\''))
		self.opponent_switch_string_probopass = "|switch|p1a: Probopass|Probopass, L92, F|100/100"
		self.opponent_switch_string_weavile = "|switch|p1a: Weavile|Weavile, L92, F|100/100"
		# see tests/test_battle.py
		self.mode = "gen9randombattle"
		self.battle_tag = "battle_tag"

		# Set up Safest battlebot
		self.safest_battlebot = SafestBattleBot(self.battle_tag)
		self.set_battle_gen_and_type(self.safest_battlebot)
		self.safest_battlebot.start_non_team_preview_battle(user_json_no_reserve_parsed, self.opponent_switch_string_probopass)

		# Set up LLM battlebot
		self.llm_battlebot = LLMBattleBot(self.battle_tag)
		self.set_battle_gen_and_type(self.llm_battlebot)
		self.llm_battlebot.start_non_team_preview_battle(user_json_no_reserve_parsed, self.opponent_switch_string_probopass)
		# pprint.pprint(self.llm_battlebot.user)

	@unittest.skip("Not implemented")
	def test_find_best_move_safest_battle_bot(self):
		best_move = self.safest_battlebot.find_best_move()
		expected = ['/choose move hydropump', '3']
		self.assertEqual(expected, best_move)

	@unittest.skip("Not implemented")
	def test_find_best_move_safest_battle_bot_should_switch(self):
		user_json = json.loads(self.user_json_one_reserve.strip('\''))
		safest_battlebot = SafestBattleBot(self.battle_tag)
		self.set_battle_gen_and_type(safest_battlebot)
		self.safest_battlebot.start_non_team_preview_battle(user_json, self.opponent_switch_string_weavile)
		best_move = self.safest_battlebot.find_best_move()
		expected_move = ['/switch 2', '3']
		self.assertEqual(expected_move, best_move)	

	@unittest.skip("Not implemented")
	def test_must_move_when_trapped(self):
		pass

	@unittest.skip("Not implemented")
	def test_no_damaging_moves_cannot_switch(self):
		pass

	@unittest.skip("Not implemented")
	def test_no_damaging_moves_should_switch(self):
		llm_battlebot_no_damaging = LLMBattleBot(self.battle_tag)
		self.set_battle_gen_and_type(llm_battlebot_no_damaging)
		json_parsed = json.loads(self.user_json_no_reserve_no_damaging_moves.strip('\''))
		llm_battlebot_no_damaging.start_non_team_preview_battle(json_parsed, self.opponent_switch_string_probopass)

		best_move = llm_battlebot_no_damaging.find_best_move()
		pass

	@unittest.skip("Not implemented")
	def test_no_remaining_pp(self):
		pass

	# @unittest.skip("Not implemented")
	def test_find_best_move_llm_battle_bot(self):
		# prompt = self.llm_battlebot.get_prompt_with_battle_context()
		# print("PROMPT\n" + prompt)
		best_move = self.llm_battlebot.find_best_move()
		# self.assertEqual(2, len(best_move))
		# self.assertTrue("hydropump" in best_move[0])

	@unittest.skip("Not implemented")
	def test_find_best_move_llm_battle_bot_user_is_choiced(self):
		pass

	@unittest.skip("Not implemented")
	def test_find_best_move_llm_battle_bot_should_switch(self):
		llm_battlebot_should_switch = LLMBattleBot(self.battle_tag)
		self.set_battle_gen_and_type(llm_battlebot_should_switch)

		user_json = json.loads(self.user_json_one_reserve.strip('\''))
		llm_battlebot_should_switch.start_non_team_preview_battle(user_json, self.opponent_switch_string_weavile)

		best_move = llm_battlebot_should_switch.find_best_move()
		self.assertEqual(2, len(best_move))
		self.assertTrue("/switch" in best_move[0])

	def set_battle_gen_and_type(self, battle: Battle):
		battle.generation = self.mode[:4]
		battle.battle_type = constants.RANDOM_BATTLE

class TestParseLLMOutput(unittest.TestCase):
    def test_parse_output_valid_move(self):
        llm_out = """CHOICE:
            'move Dragon Ascent'"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["move Dragon Ascent"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_valid_move_with_other_noise(self):
        llm_out = """LLM puts some preamble about its CHOICE:
            'move Dragon Ascent'
            Make sure we can tune out some other gibberish here."""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["move Dragon Ascent"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_valid_move_and_tera(self):
        llm_out = """CHOICE:
            'move Dragon Ascent'
            'terastallize Flying'"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["move Dragon Ascent", "terastallize Flying"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_multiple_times_picks_first_match(self):
        llm_out = """CHOICE:
            'move Dragon Ascent'
            CHOICE:
            'move Tackle'"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["move Dragon Ascent"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_move_and_switch_only_takes_move(self):
        llm_out = """CHOICE:
            'move Dragon Ascent'
            CHOICE:
            'switch Pikachu'"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["move Dragon Ascent"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_no_specified_move_should_fail(self):
        llm_out = """CHOICE:
            'move'"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = None
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_empty_string_should_fail(self):
        llm_out = ""
        parsed_out = parse_llm_output(llm_out)
        expected_out = None
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_valid_switch(self):
        llm_out = """CHOICE: 'switch Kyogre'"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["switch Kyogre"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_excess_whitespace_succeeds(self):
        llm_out = "CHOICE: \n\n'switch Kyogre'    "
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["switch Kyogre"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_no_whitespace_succeeds(self):
        llm_out = "CHOICE:'switch Kyogre'"
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["switch Kyogre"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_switch_with_no_specified_target_should_fail(self):
        llm_out = """CHOICE:
            'switch'"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = None
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_tera_with_switch_should_not_register(self):
        llm_out = """CHOICE:
            'switch Kyogre'
            'terastallize Flying'"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["switch Kyogre"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_invalid_response_format_should_fail(self):
        llm_out = """not following the expected format at all"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = None
        self.assertEqual(expected_out, parsed_out)

class TestLLMPromptFormatting(unittest.TestLoader):
	# Test for a typical scenario
	def test_format_prompt_typical_case():
		parsed_state = {
			"user": {"active": "Pikachu", "reserve": ["Charmander", "Bulbasaur"]},
			"opponent": {"active": "Squirtle", "reserve": ["Rattata"]},
		}
		user_options = ['volt tackle', 'switch Charmander', 'switch Bulbasaur']
		opponent_options = ['tackle']
		move_damages = {'volt tackle': 100}

		# Mocking ChatPromptTemplate and related methods
		with patch("showdown.battle_bots.llm.llm_helpers.ChatPromptTemplate") as MockChatPromptTemplate:
			mock_chat_template = MagicMock()
			MockChatPromptTemplate.from_messages.return_value = mock_chat_template
			mock_chat_template.format.return_value = "formatted prompt"

			# Call the function
			result = format_prompt(user_options, opponent_options, move_damages, parsed_state, 1)

			# Check that the method returns the expected result
			assert result == "formatted prompt"

			# Ensure the ChatPromptTemplate was created with the correct messages
			MockChatPromptTemplate.from_messages.assert_called_once()

			# Ensure the format method was called with the correct arguments
			mock_chat_template.format.assert_called_once_with(
				user_options=user_options,
				moves_and_damages=move_damages,
				user_reserve=["Charmander", "Bulbasaur"],
				opponent_pokemon="Squirtle",
				opponent_options=opponent_options,
				num_opp_reserve=1,
				opponent_known_reserve=["Rattata"]
			)

	def test_format_prompt_missing_user_active():
		parsed_state = {
			"user": {"reserve": ["Charmander", "Bulbasaur"]},
			"opponent": {"active": "Squirtle", "reserve": ["Rattata"]},
		}
		user_options = ['volt tackle', 'switch Charmander', 'switch Bulbasaur']
		opponent_options = ['tackle']
		move_damages = {'volt tackle': 100}

		result = format_prompt(user_options, opponent_options, move_damages, parsed_state, 1)

		# Expect the function to return None since 'active' is missing
		assert result is None

	def test_format_prompt_missing_user_options_empty():
		parsed_state = {
			"user": {"active": "Pikachu", "reserve": ["Charmander", "Bulbasaur"]},
			"opponent": {"active": "Squirtle", "reserve": ["Rattata"]},
		}
		user_options = []
		opponent_options = ['tackle']
		move_damages = {'volt tackle': 100}

		result = format_prompt(user_options, opponent_options, move_damages, parsed_state)

		# Expect the function to return None since 'active' is missing
		assert result is None

	def test_format_prompt_empty_opponent_reserve():
		parsed_state = {
			"user": {"active": "Pikachu", "reserve": ["Charmander", "Bulbasaur"]},
			"opponent": {"active": "Squirtle", "reserve": []},
		}
		user_options = ['volt tackle', 'switch Charmander', 'switch Bulbasaur']
		opponent_options = ['tackle']
		move_damages = {'volt tackle': 100}

		with patch("showdown.battle_bots.llm.llm_helpers.ChatPromptTemplate") as MockChatPromptTemplate:
			mock_chat_template = MagicMock()
			MockChatPromptTemplate.from_messages.return_value = mock_chat_template
			mock_chat_template.format.return_value = "formatted prompt"

			result = format_prompt(user_options, opponent_options, move_damages, parsed_state, 0)

			assert result == "formatted prompt"
			mock_chat_template.format.assert_called_once_with(
				user_options=user_options,
				moves_and_damages=move_damages,
				user_reserve=["Charmander", "Bulbasaur"],
				opponent_pokemon="Squirtle",
				opponent_options=opponent_options,
				num_opp_reserve=0,
				opponent_known_reserve=[]
			)
