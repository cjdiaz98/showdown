
import unittest
from collections import defaultdict

from showdown.Commentary.LLMCommentator import *

class TestChoiceRepresentations(unittest.TestCase):		
	def test_pokemon_dragged_representation(self):
		# to do
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