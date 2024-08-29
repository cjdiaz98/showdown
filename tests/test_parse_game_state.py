import unittest
from collections import defaultdict

import constants
from showdown.engine.damage_calculator import _calculate_damage
from showdown.engine.damage_calculator import calculate_damage
from showdown.engine.objects import Pokemon, Side, State
from showdown.Commentary.parsingUtils import parse_pokemon, parse_side, parse_state, parse_move_data
from showdown.battle import Pokemon as StatePokemon
from data import all_move_json
import pprint

class TestCalculateDamageAmount(unittest.TestCase):
	expected_charizard_dict = {
			'id': 'charizard',
			'level': 100,
			'types': ['fire', 'flying'],
			'current_hp_percentage': 100.0,
			'ability': "blaze",
			'item': 'unknown_item',
			'attack': 225,
			'defense': 213,
			'special-attack': 275,
			'special-defense': 227,
			'speed': 257,
			'attack_boost': 0,
			'defense_boost': 0,
			'special_attack_boost': 0,
			'special_defense_boost': 0,
			'speed_boost': 0,
			'accuracy_boost': 0,
			'evasion_boost': 0,
			'status': None,
			'terastallized': False,
			'volatileStatus': [],
			'moves': ["flamethrower", "flareblitz", "flamewheel", "reflect"],
		}
	
	expected_venusaur_dict = {
		'id': 'venusaur',
		'level': 100,
		'types': ['grass', 'poison'],
		'current_hp_percentage': 100.0,
		'ability': 'chlorophyll',
		'item': 'unknown_item',
		'attack': 221,
		'defense': 223,
		'special-attack': 257,
		'special-defense': 257,
		'speed': 217,
		'attack_boost': 0,
		'defense_boost': 0,
		'special_attack_boost': 0,
		'special_defense_boost': 0,
		'speed_boost': 0,
		'accuracy_boost': 0,
		'evasion_boost': 0,
		'status': None,
		'terastallized': False,
		'volatileStatus': [],
		'moves': ['solarbeam', 'sludgebomb', 'sleeppowder', 'synthesis']
	}

	expected_blastoise_dict = {
		'id': 'blastoise',
		'level': 100,
		'types': ['water'],
		'current_hp_percentage': 100.0,
		'ability': "torrent",
		'item': 'unknown_item',
		'attack': 223,
		'defense': 257,
		'special-attack': 227,
		'special-defense': 267,
		'speed': 213,
		'attack_boost': 0,
		'defense_boost': 0,
		'special_attack_boost': 0,
		'special_defense_boost': 0,
		'speed_boost': 0,
		'accuracy_boost': 0,
		'evasion_boost': 0,
		'status': None,
		'terastallized': False,
		'volatileStatus': [],
		'moves': ["hydropump", "icebeam", "rapidspin", "protect"]
	}

	expected_blaziken_dict = {
		'id': 'blaziken',
		'level': 100,
		'types': ['fire', 'fighting'],
		'current_hp_percentage': 100.0,
		'ability': 'speed boost',
		'item': 'unknown_item',
		'attack': 297,
		'defense': 197,
		'special-attack': 277,
		'special-defense': 197,
		'speed': 217,
		'attack_boost': 0,
		'defense_boost': 0,
		'special_attack_boost': 0,
		'special_defense_boost': 0,
		'speed_boost': 0,
		'accuracy_boost': 0,
		'evasion_boost': 0,
		'status': None,
		'terastallized': False,
		'volatileStatus': [],
		'moves': ['blazekick', 'highjumpkick', 'protect', 'swordsdance']
	}

	def setUp(self):
		self.maxDiff = None
		self.charizard = StatePokemon("charizard", 100)
		self.charizard.ability = "blaze"
		self.charizard.moves = [
			{constants.ID: 'flamethrower'},
			{constants.ID: 'flareblitz'},
			{constants.ID: 'flamewheel'},
			{constants.ID: 'reflect'},
		]

		self.venusaur = StatePokemon("venusaur", 100)
		self.venusaur.ability = "chlorophyll"
		self.venusaur.moves = [
			{constants.ID: 'solarbeam'},
			{constants.ID: 'sludgebomb'},
			{constants.ID: 'sleeppowder'},
			{constants.ID: 'synthesis'},
		]

		self.blastoise = StatePokemon("blastoise", 100)
		self.blastoise.ability = "torrent"
		self.blastoise.moves = [
			{constants.ID: 'hydropump'},
			{constants.ID: 'icebeam'},
			{constants.ID: 'rapidspin'},
			{constants.ID: 'protect'},
		]

		self.typhlosion = StatePokemon("typhlosion", 100)
		self.typhlosion.ability = "flash fire"
		self.typhlosion.moves = [
			{constants.ID: 'eruption'},
			{constants.ID: 'flamethrower'},
			{constants.ID: 'focusblast'},
			{constants.ID: 'hiddenpower'},
		]

		self.meganium = StatePokemon("meganium", 100)
		self.meganium.ability = "overgrow"
		self.meganium.moves = [
			{constants.ID: 'leafstorm'},
			{constants.ID: 'earthquake'},
			{constants.ID: 'reflect'},
			{constants.ID: 'synthesis'},
		]

		self.feraligatr = StatePokemon("feraligatr", 100)
		self.feraligatr.ability = "torrent"
		self.feraligatr.moves = [
			{constants.ID: 'waterfall'},
			{constants.ID: 'icepunch'},
			{constants.ID: 'dragondance'},
			{constants.ID: 'crunch'},
		]

		self.blaziken = StatePokemon("blaziken", 100)
		self.blaziken.ability = "speed boost"
		self.blaziken.moves = [
			{constants.ID: 'blazekick'},
			{constants.ID: 'highjumpkick'},
			{constants.ID: 'protect'},
			{constants.ID: 'swordsdance'},
		]

		# self.battle = Battle()
		reserve = [self.venusaur, self.blastoise, self.typhlosion, self.meganium, self.feraligatr]
		self.our_side = Side(self.charizard, [self.venusaur], False, dict(), False)
		self.opponent_side = Side(self.blaziken, [self.blastoise], False, dict(), False)
		
	def test_parse_pokemon(self):
		self.assertEqual(self.expected_charizard_dict, parse_pokemon(self.charizard))

	def test_parse_side_team_hazards_active(self):
		test_side = Side(self.charizard, [self.venusaur, self.blastoise], False, dict(), False)
		test_side.side_conditions[constants.LIGHT_SCREEN] = 1
		test_side.side_conditions[constants.SPIKES] = 2
		expected_dict =  {
			"active": self.expected_charizard_dict,
			"reserve": [self.expected_venusaur_dict, self.expected_blastoise_dict],
			"wish active": False,
			"side conditions": {
				constants.LIGHT_SCREEN: 1,
				constants.SPIKES: 2,
			},
			"future sight active": False
		}
		self.assertEqual(expected_dict, parse_side(test_side))

	def test_parse_side_no_reserve(self):
		test_side = Side(self.charizard, [], False, dict(), False)
		expected_dict =  {
			"active": self.expected_charizard_dict,
			"reserve": [],
			"wish active": False,
			"side conditions": {},
			"future sight active": False
		}
		self.assertEqual(expected_dict, parse_side(test_side))
		
	def test_parse_side_wish_and_future_sight_active(self):
		test_side = Side(self.charizard, [], True, dict(), True)
		expected_dict =  {
			"active": self.expected_charizard_dict,
			"reserve": [],
			"wish active": True,
			"side conditions": {},
			"future sight active": True
		}
		self.assertEqual(expected_dict, parse_side(test_side))

	def test_parse_game_state(self):
		state = State(self.our_side, self.opponent_side, None, None, None)
		expected_state_dict = {
			"self": {
				"active": self.expected_charizard_dict,
				"reserve": [self.expected_venusaur_dict],
				"wish active": False,
				"side conditions": {},
				"future sight active": False
			},
			"opponent": {
				"active": self.expected_blaziken_dict,
				"reserve": [self.expected_blastoise_dict],
				"wish active": False,
				"side conditions": {},
				"future sight active": False
			},
			constants.WEATHER: None,
			constants.FIELD: None,
			constants.TRICK_ROOM: None
		}
		self.assertEqual(expected_state_dict, parse_state(state))
	
	def test_parse_game_state_additional_conditions(self):
		state = State(self.our_side, self.opponent_side, constants.RAIN, constants.GRASSY_TERRAIN, True)
		
		expected_state_dict = {
			"self": {
				"active": self.expected_charizard_dict,
				"reserve": [self.expected_venusaur_dict],
				"wish active": False,
				"side conditions": {},
				"future sight active": False
			},
			"opponent": {
				"active": self.expected_blaziken_dict,
				"reserve": [self.expected_blastoise_dict],
				"wish active": False,
				"side conditions": {},
				"future sight active": False
			},
			constants.WEATHER: constants.RAIN,
			constants.FIELD: constants.GRASSY_TERRAIN,
			constants.TRICK_ROOM: True
		}

		self.assertEqual(expected_state_dict, parse_state(state))

	def test_get_move_data(self):
		expected_move_data = {
			'name': 'flamethrower',
			'accuracy': 100,
			'basePower': 90,
			'category': 'special',
			'priority': 0,
			'target': 'normal',
			'type': 'fire'
		}
		self.assertEqual(expected_move_data, parse_move_data(all_move_json["flamethrower"]))

	def test_get_move_data_status_condition(self):
		expected_move_data = {
			'name': 'flamethrower',
			'accuracy': 100,
			'basePower': 90,
			'category': 'special',
			'priority': 0,
			'target': 'normal',
			'type': 'fire'
		}
		self.assertEqual(expected_move_data, parse_move_data(all_move_json["flamethrower"]))

	def test_parse_move_data_boost_move(self):
		expected_move_data = {
			'name': 'swordsdance',
			'accuracy': True,
			'basePower': 0,
			'category': 'status',
			'priority': 0,
			'target': 'self',
			'type': 'normal',
			'boosts': {
				'attack': 2
			}
		}

		self.assertEqual(expected_move_data, parse_move_data(all_move_json["swordsdance"]))

	def test_parse_move_data_status_move(self):
		expected_move_data = {
			'name': 'thunderwave',
			'accuracy': 90,
			'basePower': 0,
			'category': 'status',
			'priority': 0,
			'target': 'normal',
			'type': 'electric',
			'status': 'par'
		}

		self.assertEqual(expected_move_data, parse_move_data(all_move_json["thunderwave"]))
