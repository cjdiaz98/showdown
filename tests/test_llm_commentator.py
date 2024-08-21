
import unittest
from collections import defaultdict

from showdown.LLMCommentator import *

class TestChoiceRepresentations(unittest.TestCase):
	def test_pokemon_choice_dict_representation_target_status_move(self):
		# to do
		#|move|p1a: Oddish|Sleep Powder|p2b: Pikachu
		#|-status|p2b: Pikachu|slp
		expected_dict = {
			"pokemon": "Oddish",
			"actor": "p1",
			"choice": "move",
			"move details": {
				"name": "Sleep Powder",
				"category": "status",
				"hit target": True,
				"move failed": False,
				"target": "Pikachu",
				"effects": {
					"status": "slp"
				}
			}
		}
		options = None
		self.assertEqual(expected_dict, options)
		
	def test_pokemon_choice_dict_representation_self_status_move_stat_boost(self):
		# to do
		# |move|p1a: Sableye|Calm Mind|p1a: Sableye
		# |-boost|p1a: Sableye|spa|1
		# |-boost|p1a: Sableye|spd|1
		expected_dict = {
			"pokemon": "Sableye",
			"actor": "p1",
			"choice": "move",
			"move details": {
				"name": "Calm Mind",
				"category": "status",
				"hit target": True,
				"target": "self",
				"move failed": False,
				"effects": {
					"boosts": {
						"spa": 1,
						"spd": 1
					}
				}
			}
		}
		options = None
		self.assertEqual(expected_dict, options)	
		
	def test_pokemon_choice_dict_representation_target_status_hazards(self):
		# to do
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

	def test_pokemon_choice_dict_representation_target_physical_move(self):
		# to do
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		
	def test_pokemon_choice_dict_representation_target_move_miss(self):
		# to do
		# |move|p1a: Whimsicott|Stun Spore|p2a: Tentacruel|[miss]
		# |-miss|p1a: Whimsicott|p2a: Tentacruel
		expected_dict = {
			"pokemon": "Whimsicott",
			"actor": "p1",
			"choice": "move",
			"move details": {
				"name": "Stun Spore",
				"category": "status",
				"hit target": False,
				"target": "Tentacruel",
				"move failed": False,
			}
		}
		options = None
		self.assertEqual(expected_dict, options)
				
	def test_pokemon_choice_dict_representation_target_attack_stat_drop_effect_on_target(self):
		# to do
		# |move|p2a: Golem|Rock Tomb|p1a: Gyarados
		# |-supereffective|p1a: Gyarados
		# |-damage|p1a: Gyarados|55/220
		# |-unboost|p1a: Gyarados|spe|1
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		
		
	def test_pokemon_choice_dict_representation_attack_that_switches_user(self):
		# to do
		# |move|p2a: Forretress|Volt Switch|p1a: Heracross
		# |-damage|p1a: Heracross|121/190|
		# |switch|p2a: Vileplume|Vileplume, L62, F|192/192
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

	def test_pokemon_choice_dict_representation_attack_KOs_target(self):
		# to do
		# |move|p1a: Nidoking|Ice Beam|p2a: Diggersby
		# |-supereffective|p2a: Diggersby
		# |-damage|p2a: Diggersby|0 fnt
		# |faint|p2a: Diggersby
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

		
	def test_damage_from_item(self):
		# to do - |-damage|p1a: Nidoking|36/270|[from] item: Life Orb
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)	
		
	def test_pokemon_choice_dict_representation_switch_user_take_hazard_damage(self):
		# to do
		# |switch|p1a: Steelix|Steelix, L62, F, shiny|222/222
		# |-damage|p1a: Steelix|195/222|[from] Spikes
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		
	def test_pokemon_dragged_representation(self):
		# to do
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

	def test_pokemon_choice_dict_representation_switch_user_ability_takes_effect(self):
		# to do - e.g. intimidate on switch in
		# |switch|p1a: Genesect-Douse|Genesect-Douse|314/314
		# |-boost|p1a: Genesect-Douse|spa|1|[from] ability: Download
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		
	def test_switch_new_pokemon_after_faint(self):
		# to do - |switch|p2a: Lugia|Lugia, L72|100/100
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		# check that we always display HP out of 100		
		
	def test_pokemon_change_forms_mega(self):
		# |detailschange|p1a: Sableye|Sableye-Mega, L87, M
		# |-mega|p1a: Sableye|Sableye|Sablenite
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		
	def test_pokemon_change_forms_ability(self):
		# |-formechange|p2b: earl sweatshirt|Aegislash
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

class TestPokemonRepresentations(unittest.TestCase):
	def test_pokemon_dict_representation_normal(self):
		# to do 
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		# check that we always display HP out of 100
	
	def test_pokemon_dict_representation_status_afflicted(self):
		# to do
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		
	def test_pokemon_dict_representation_volatile_status_afflicted(self):
		# to do
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		
	def test_pokemon_dict_representation_stat_boosts(self):
		# to do
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		
	def test_pokemon_dict_representation_fainted(self):
		# to do
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

class TestBattleStateRepresentations(unittest.TestCase):
	def test_battle_start(self):
		# to do - 
		# |start
		# |switch|p1a: Greninja|Greninja, M|285/285
		# |switch|p2a: Zapdos|Zapdos, shiny|321/321
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
			
	def test_battle_victory(self):
		# to do - 
		# |win|cjflex8
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

	def test_battle_draw(self):
		# to do
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

	def test_battle_forfeit(self):
		# to do
		# |callback|decision
		# |-message|Onox forfeited.
		# |
		# |win|kdarewolf
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		
	def test_battle_track_pokemon_counts(self):
		# to do - how many pokemon each person has left
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

class TestEndOfTurnRepresentations(unittest.TestCase):
	def test_take_damage_from_status(self):
		# to do - |-damage|p1a: Lunala|269/316 tox|[from] psn
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		
	def test_heal(self):
		# to do - 
		# |-heal|p2a: Regice|49/100|[from] Grassy Terrain
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

	def test_damage_from_weather(self):
		# to do - |-heal|p2a: Regice|49/100|[from] Grassy Terrain
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)
		# check that we always display HP out of 100