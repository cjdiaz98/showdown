import unittest
from collections import defaultdict

import constants
from showdown.battle import Battle
from showdown.battle_bots.llm.main import BattleBot as LLMBattleBot
from showdown.battle_bots.llm.llm_helpers import parse_llm_output
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

	def test_find_best_move_safest_battle_bot(self):
		best_move = self.safest_battlebot.find_best_move()
		expected = ['/choose move hydropump', '3']
		self.assertEqual(expected, best_move)

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

	def test_find_best_move_llm_battle_bot(self):
		# prompt = self.llm_battlebot.get_prompt_with_battle_context()
		# print("PROMPT\n" + str(prompt))
		best_move = self.llm_battlebot.find_best_move()
		print(best_move)
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
