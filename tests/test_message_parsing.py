
import unittest
import pprint
from showdown.LLMCommentator import *

class TestChoiceRepresentations(unittest.TestCase):
	# def setUp(self):
	# 	self.skipTest('module not tested') # uncomment when you want to skip tests

	def test_parse_move(self):
		move = "|move|p1a: Tornadus|Heat Wave|p2a: Regice|[miss]"
		expected_dict = {
			"choice": "move",
			"trainer": "p1a",
			"pokemon": "Tornadus",
			"name": "Heat Wave",
			"target": "Regice",
			"missed": True,
			"category": "special",
			"move failed": False
		}
		parsed = parseUseMove(move)
		self.assertEqual(expected_dict, parsed)

	def test_pokemon_choice_dict_representation_target_special_move_no_miss(self):
		move = "|move|p1a: Nidoking|Earth Power|p2a: Diggersby"
		expected_dict = {
			"choice": "move",
			"trainer": "p1a",
			"pokemon": "Nidoking",
			"name": "Earth Power",
			"target": "Diggersby",
			"missed": False,
			"category": "special",
			"move failed": False
		}
		self.assertEqual(expected_dict, parseUseMove(move))	

	def test_pokemon_choice_dict_representation_self_status_move_stat_boost(self):
		move = "|move|p1a: Sableye|Calm Mind|p1a: Sableye"
		expected_dict = {
			"choice": "move",
			"trainer": "p1a",
			"pokemon": "Sableye",
			"name": "Calm Mind",
			"target": "self",
			"missed": False,
			"category": "status",
			"move failed": False
		}
		self.assertEqual(expected_dict, parseUseMove(move))	

	def test_pokemon_choice_dict_representation_switch_user(self):
		choice = "|switch|p2a: Diggersby|Diggersby, L83, M|100/100"
		expected_dict = {
			"choice": "switch",
			"trainer": "p2a",
			"switched in": "Diggersby",
			"hp": "100/100"
		}
		
		self.assertEqual(expected_dict, parseSwitchOrDrag(choice))

	def test_pokemon_cant_move(self):
		choice = "|cant|p2a: Dodrio|par"
		expected_dict = {
			"choice": "can't move",
			"trainer": "p2a",
			"pokemon": "Dodrio",
			"reason": "par"
		}
		
		self.assertEqual(expected_dict, parseCantMove(choice))

	def test_parse_damage(self):
		event_dict = dict()
		damage = "|-damage|p1a: Sableye|324/360"
		expected_dict = {
			"damage": {
			# "trainer": "p1a",
			"target": "Sableye",
			"new hp": "90/100"
			}
		}
		result = parseDamageOrHeal(damage, event_dict)
		self.assertEqual(expected_dict, result)

	def test_parse_damage_with_condition(self):
		text = "|-damage|p1a: Gardevoir|162/309 par|[from] confusion"
		expected_dict = {
			"damage": {
			"target": "Gardevoir",
			"new hp": "53/100",
			"source": {
				"factor": "confusion"
				}
			}
		}
		event_dict = dict()
		self.assertEqual(expected_dict, parseDamageOrHeal(text, event_dict))

	def test_parse_damage_from_source(self):
		event_dict = dict()
		damage = "|-heal|p1a: Tyrantrum|156/339|[from] item: Leftovers"
		expected_dict = {
			"heal": {
			# "trainer": "p1a",
			"target": "Tyrantrum",
			"new hp": "47/100",
			"source": {
				"factor": "item: Leftovers"
				}
			}
		}
		result = parseDamageOrHeal(damage, event_dict)
		self.assertEqual(expected_dict, result)


	def test_pokemon_choice_dict_representation_attack_super_effective_on_target(self):
		# to do
		msg = """|move|p1a: Sableye|Dark Pulse|p2a: Banette
		\n#|-supereffective|p2a: Banette"""
		expected_events = [
			{
			"choice": "move",
			"trainer": "p1a",
			"pokemon": "Sableye",
			"name": "Dark Pulse",
			"target": "Banette",
			"missed": False,
			"category": "special",  # Dark Pulse is a special move
			"move failed": False,
			"effectiveness": "supereffective",
			}			
		]
		result = parseMessagesIntoEventDicts(msg)
		self.assertEqual(expected_events, result)
	
	def test_pokemon_choice_dict_representation_attack_no_effect_on_target(self):
		move = """|move|p2a: Hitmonlee|Mach Punch|p1a: Sableye
		\n|-immune|p1a: Sableye"""
		expected_events = [
			{
				"choice": "move",
				"trainer": "p2a",
				"pokemon": "Hitmonlee",
				"name": "Mach Punch",
				"target": "Sableye",
				"missed": False,
				"category": "physical",  # Mach Punch is a physical move
				"move failed": False,
				"effectiveness": "immune",  # Sableye is immune to Mach Punch
			}
		]
		result = parseMessagesIntoEventDicts(move)
		self.assertEqual(expected_events, result)

	def test_pokemon_choice_dict_representation_attack_with_damage_on_target(self):
		move = """|move|p2a: Hitmonlee|Thunder Punch|p1a: Ampharos
		\n|-resisted|p1a: Ampharos
		\n|-damage|p1a: Ampharos|348/360"""
		expected_events = [
			{
				"choice": "move",
				"trainer": "p2a",
				"pokemon": "Hitmonlee",
				"name": "Thunder Punch",
				"target": "Ampharos",
				"missed": False,
				"category": "physical",  # Thunder Punch is a physical move
				"move failed": False,
				"effectiveness": "resisted",  # Ampharos resisted the move
				"damage": {
				"target": "Ampharos",
				"new hp": "97/100"
				}
			}
		]
		result = parseMessagesIntoEventDicts(move)
		self.assertEqual(expected_events, result)

	def test_crit_dict_representation(self):
		move = "|move|p2a: Tentacruel|Scald|p1a: Tentacruel\n|-crit|p1a: Tentacruel\n|-resisted|p1a: Tentacruel"
		expected_events = [
			{
				"choice": "move",
				"trainer": "p2a",
				"pokemon": "Tentacruel",
				"name": "Scald",
				"target": "Tentacruel",
				"missed": False,
				"category": "special", 
				"move failed": False,
				"critical hit": True,
				"effectiveness": "resisted",
			}
		]	
		result = parseMessagesIntoEventDicts(move)
		self.assertEqual(expected_events, result)	

	def test_pokemon_choice_dict_representation_target_attack_status_effect(self):
		move = """|move|p2a: Swampert|Scald|p1a: Whimsicott
		|-resisted|p1a: Whimsicott
		|-damage|p1a: Whimsicott|157/323
		|-status|p1a: Whimsicott|brn"""

		expected_events = [
			{
				"choice": "move",
				"trainer": "p2a",
				"pokemon": "Swampert",
				"name": "Scald",
				"target": "Whimsicott",
				"missed": False,
				"category": "special",  # Scald is a special move
				"move failed": False,
				"effectiveness": "resisted",  # Whimsicott resisted the move
				"damage": {
					"target": "Whimsicott",
					"new hp": "49/100"
				},
				"status": {
					"target": "Whimsicott",
					"condition": "brn"  # Whimsicott was burned
				}
			}
		]
		self.assertEqual(expected_events, parseMessagesIntoEventDicts(move))

	def test_pokemon_choice_dict_representation_target_attack_stat_drop_effect_on_self(self):
		# to do 
		move = """|move|p1a: Nidoking|Superpower|p2a: Hitmonlee
		|-damage|p2a: Hitmonlee|4/100
		|-unboost|p1a: Nidoking|atk|1
		|-unboost|p1a: Nidoking|def|1"""

		expected_events = [
			{
				"choice": "move",
				"trainer": "p1a",
				"pokemon": "Nidoking",
				"name": "Superpower",
				"target": "Hitmonlee",
				"missed": False,
				"category": "physical",  # Superpower is a physical move
				"move failed": False,
				"damage": {
					"target": "Hitmonlee",
					"new hp": "4/100"
				},
				"stat changes": [
					{
						"pokemon": "Nidoking",
						"stat": "attack",
						"change": -1  # Attack decreased by 1 stage
					},
					{
						"pokemon": "Nidoking",
						"stat": "defense",
						"change": -1  # Defense decreased by 1 stage
					}
				]
			}
		]
		result = parseMessagesIntoEventDicts(move)
		# pprint.pprint(result)
		self.assertEqual(expected_events, result)

	def test_parse_unboost(self):
		unboost_evt = "|-unboost|p1a: Nidoking|atk|1"
		unboost_event_dict = {}
		unboost_expected_dict = {
			"stat changes": [
				{
					"pokemon": "Nidoking",
					"stat": "attack",
					"change": -1  # Attack decreased by 1 stage
				}
			]
		}
		self.assertEqual(unboost_expected_dict, parseBoostUnboost(unboost_evt, unboost_event_dict))

		boost_evt = "|-boost|p1a: Mewtwo|spa|2"
		boost_event_dict = {}
		boost_expected_dict = {
			"stat changes": [
				{
					"pokemon": "Mewtwo",
					"stat": "special attack",
					"change": 2 
				}
			]
		}
		self.assertEqual(boost_expected_dict, parseBoostUnboost(boost_evt, boost_event_dict))

	def test_parse_faint(self):
		faint = "|faint|p1a: Sableye"
		expected_dict = {
			"event": "faint",
			"pokemon": "Sableye"
		}
		self.assertEqual(expected_dict, parseFaint(faint))

	def test_inactivity_due_to_status(self):
		msg = "|cant|p2b: Oddish|slp"
		expected_dict = {
			"choice": "can't move",
			"trainer": "p2b",
			"pokemon": "Oddish",
			"reason": "slp"  # Sleep
		}
		self.assertEqual(expected_dict, parseCantMove(msg))
		
	def test_inactivity_due_to_volatile_status(self):
		msg = "|cant|p1a: Hippowdon|move: Taunt|Stealth Rock"
		expected_dict = {
			"choice": "can't move",
			"trainer": "p1a",
			"pokemon": "Hippowdon",
			"reason": "move: Taunt"  # Taunted, unable to use Stealth Rock
		}
		self.assertEqual(expected_dict, parseCantMove(msg))
	
	def test_inactivity_due_to_flinch(self):
		msg = "|cant|p1a: Edward|flinch"
		expected_dict = {
			"choice": "can't move",
			"trainer": "p1a",
			"pokemon": "Edward",
			"reason": "flinch"  # Flinched, can't move
		}
		self.assertEqual(expected_dict, parseCantMove(msg))

	def test_terrain_take_effect(self):
		text = "|-fieldstart|move: Grassy Terrain|[from] ability: Grassy Surge|[of] p2a: Tapu Bulu"
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

	def test_terrain_effect_end(self):
		text = "|-fieldend|move: Grassy Terrain|[from] ability: Psychic Surge|[of] p2a: Indeedee"
		expected_dict = {}
		options = None
		self.assertEqual(expected_dict, options)

	def test_terrain_take_effect(self):
		text = "|-fieldstart|move: Grassy Terrain|[from] ability: Grassy Surge|[of] p2a: Tapu Bulu"
		expected_dict = {
			"field event": "fieldstart",
			"field": "Grassy Terrain",
			"source": {
				"factor": "ability: Grassy Surge",
				"pokemon": "Tapu Bulu"
			}
		}
		self.assertEqual(expected_dict, parseFieldStartOrEnd(text))

	def test_terrain_effect_end(self):
		text = "|-fieldend|move: Grassy Terrain|[from] ability: Psychic Surge|[of] p2a: Indeedee"
		expected_dict = {
			"field event": "fieldend",
			"field": "Grassy Terrain",
			"source": {
				"factor": "ability: Psychic Surge",
				"pokemon": "Indeedee"
			}
		}
		self.assertEqual(expected_dict, parseFieldStartOrEnd(text))

	def test_volatile_status_start(self):
		text = "|-start|p1a: Sableye|confusion"
		event_dict = {}
		expected_dict = {
			"volatile status": {
				"event": "start",
				"target": "Sableye",
				"status": "confusion"
			}
		}
		self.assertEqual(expected_dict, parseVolatileStatus(text, event_dict))

	def test_volatile_status_end(self):
		text = "|-end|p1a: Sableye|confusion"
		event_dict = {}
		expected_dict = {
			"volatile status": {
				"event": "end",
				"target": "Sableye",
				"status": "confusion"
			}
		}
		self.assertEqual(expected_dict, parseVolatileStatus(text, event_dict))

	def test_weather(self):
		text = "|-weather|RainDance|[upkeep]"
		event_dict = {}
		expected_dict = {
			"weather": "rain"
		}
		self.assertEqual(expected_dict, parseWeather(text, event_dict))		

	def test_weather_sun(self):
		text = "|-weather|SunnyDay|[upkeep]"
		event_dict = {}
		expected_dict = {
			"weather": "sun"
		}
		self.assertEqual(expected_dict, parseWeather(text, event_dict))		

	def test_weather_none(self):
		text = "|-weather|none"
		event_dict = {}
		expected_dict = {
			"weather": "none"
		}
		self.assertEqual(expected_dict, parseWeather(text, event_dict))		


class TestExpressHPOutOf100(unittest.TestCase):
	# def setUp(self):
	# 	self.skipTest('module not tested') # uncomment when you want to skip tests

	def test_full_hp(self):
		self.assertEqual(expressHPOutOf100("100/100"), "100/100")

	def test_zero_hp(self):
		self.assertEqual(expressHPOutOf100("0/100"), "0/100")

	def test_partial_hp(self):
		self.assertEqual(expressHPOutOf100("348/360"), "97/100")

	def test_one_hp(self):
		self.assertEqual(expressHPOutOf100("1/100"), "1/100")

	def test_large_hp_values(self):
		self.assertEqual(expressHPOutOf100("500/1000"), "50/100")

	def test_rounding_up(self):
		self.assertEqual(expressHPOutOf100("51.5/100"), "52/100")

	def test_faint(self):
		self.assertEqual(expressHPOutOf100("0 fnt"), "0/100")

class TestParseFromLogFile(unittest.TestCase):
	@unittest.skip("skip")
	def test_parseFromLogFile(self):
		result = parse_turns_from_file("C:\\Users\\cjdia\\Desktop\\Study\\PokemonShowdown\\singles_forfeit.txt")
		# result = parse_turns_from_file("C:\\Users\\cjdia\\Desktop\\Study\\PokemonShowdown\\singles_forfeit_short.txt")
		# pprint.pprint(result)
		write_file = "C:\\Users\\cjdia\\Desktop\\Study\\PokemonShowdown\\parsed_singles_forfeit.txt"
		with open(write_file, 'w') as f:
			pprint.pprint(result, stream=f)
		f.close()