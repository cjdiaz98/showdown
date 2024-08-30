from config import ShowdownConfig
from showdown.battle import Pokemon, LastUsedMove, Side, State
from showdown.engine.objects import Pokemon as TransposePokemon
from showdown.battle_bots.helpers import get_move_relevant_data
import constants
from data import all_move_json
import math
import pprint
import json 

BOOST_NAMES = {
	"atk": "attack",
	"def": "defense",
	"spa": "special attack",
	"spd": "special defense",
	"spe": "speed",
	"acc": "accuracy",
	"eva": "evasion"
}

def parseMessagesIntoEventDicts(msg: str) -> list[dict]:
	# to do: parse messages into dict
	msg_lines = msg.split('\n')

	events = []
	action = None
	event_dict = None
	for i, line in enumerate(msg_lines):
		split_msg = line.split('|')
		# print(line + "\n")
		if len(split_msg) < 2:
			continue

		action = split_msg[1].strip()
		if action.startswith("-") and event_dict is not None:
			# this is a subevent. Add it to the main event dict
			# print("subevent " + action)
			function_to_call = subevent_parser_lookup.get(action)
			if function_to_call is not None:
				function_to_call(line, event_dict)
			
		else:
			# This is a main event
			# print("main event " + action)
			if event_dict is not None:
				# append the previous main event to the list of events
				events.append(event_dict)
			event_dict = None
			function_to_call = main_event_parser_lookup.get(action)
			if function_to_call is not None:
				event_dict = function_to_call(line)
	
	if event_dict is not None:
		events.append(event_dict)
	return events

def pokemonDictRepresentation(pkm: Pokemon) -> dict:
	attributes_of_interest = ['name','level', 'types', 'hp', 'max_hp', 'status', 'volatile_status']

	pkm_dict = {attr: getattr(pkm, attr) for attr in attributes_of_interest}

	boosts = dict()
	for boost_name in BOOST_NAMES.values():
		boost = getattr(pkm, boost_name)
		if boost != 0:
			boosts[boost_name] = boost
	pkm_dict["boosts"] = boosts

def parseSwitchOrDrag(msg: str) -> dict:
	split_msg = msg.split('|')[1:]
	switched_in = split_msg[2].split(',')[0]
	hp = expressHPOutOf100(parseOutHPString(msg))
	switch_dict = {
		"choice": "switch", # to do: or drag??
		"trainer": split_msg[1].split(':')[0],
		"switched in": switched_in,
		"hp": hp
	}
	return switch_dict

def parseUseMove(msg: str) -> dict:
	# |move|p2a: Crobat|Taunt|p1a: Hippowdon
	# |move|p1a: Tornadus|Heat Wave|p2a: Regice|[miss]
	split_msg = msg.split('|')[1:]
	trainer = split_msg[1].split(':')[0].strip()
	user = split_msg[1].split(':')[1].strip()
	move_name = split_msg[2].strip()
	target = split_msg[3].split(':')[1].strip()
	missed = "[miss]" in msg

	move_name_key = move_name.replace(' ', '').lower()
	if move_name_key not in all_move_json:
		return None
	
	move_info = all_move_json[move_name_key]

	move_dict = {
		"choice": "move",
		"trainer": trainer,
		"pokemon": user,
		"name": move_name,
		"target": target,
		"category": move_info["category"],
		"move failed": False, # to do
		"missed": missed
	}

	if move_info["target"] == "self":
		move_dict["target"] = "self"
	
	return move_dict

def parseFormChange(msg: str) -> dict:
	return {}

def parseMoveEffectiveness(msg: str, event_dict: dict) -> dict:
	# to do: parse attack move
	# |-supereffective|p2a: Diggersby
	split_msg = msg.split('|')
	event_dict["effectiveness"] = split_msg[1].replace('-', '')
	return event_dict

def parseDamageOrHeal(msg: str, event_dict: dict) -> dict:
	# print("parseDamageOrHeal")
	split_msg = msg.split('|')
	if len(split_msg) >= 4:
		hp_event_type = split_msg[1].replace('-', '') # heal or damage
		trainer, target = parseTrainerandPokemon(split_msg[2])
		hp_event_info = {
			"event": hp_event_type,
			"trainer": trainer,
			"target": target.strip(),
			"new hp": expressHPOutOf100(parseOutHPString(msg)),
		}
		if "[from]" in msg:
			# e.g. [from] item: Leftovers
			hp_event_info["source"] = parseSource(msg)

		if event_dict.get("hp events") is None:
			event_dict["hp events"] = []
		event_dict["hp events"].append(hp_event_info)
	return event_dict

def parseCrit(msg: str, event_dict: dict) -> dict:
	if "-crit" in msg:
		event_dict["critical hit"] = True

def parseCantMove(msg: str) -> dict:
	# Split the input string based on the "|" delimiter
	parts = msg.split("|")
	
	# Extract trainer and reason from the second and third parts
	trainer, pokemon = parseTrainerandPokemon(parts[2])
	reason = parts[3]

	# Populate the event_dict with the parsed information
	event_dict = {
		"choice": 'can\'t move',
		"trainer": trainer,
		"pokemon": pokemon,
		"reason": reason
	}

	return event_dict

def parseFaint(msg: str) -> dict:
	split_msg = msg.split('|')
	fainted_pokemon = split_msg[2].split(':')[1]
	faint_dict = {
		"event": "faint",
		"pokemon": fainted_pokemon.strip()
	}
	return faint_dict

def parseStatus(msg: str, event_dict: dict) -> dict:
	# |-status|p1a: Whimsicott|brn
	split_msg = msg.split('|')
	trainer, target = parseTrainerandPokemon(split_msg[2])
	status = split_msg[3]
	event_dict["status"] = {
		"target": target.strip(),
		"condition": status
	}

	return event_dict

def parseBoostUnboost(event_str: str, event_dict: dict) -> dict:
	# Split the event string by "|" to get individual components
	parts = event_str.split("|")
	
	event_name = "boost"
	# Determine if it's a boost or unboost event
	if parts[1] == "-boost":
		change = int(parts[4])  # Positive stat change
	elif parts[1] == "-unboost":
		change = -int(parts[4])  # Negative stat change
		event_name = "drop"
	
	# Extract the trainer, pokemon, stat, and change
	trainer_pokemon = parts[2].split(": ")
	pokemon = trainer_pokemon[1]  # Extract the pokemon name
	stat_short = parts[3]  # Stat shorthand (e.g., "atk", "spa")
	
	# Convert stat shorthand to full name using BOOST_NAMES dictionary
	stat_full = BOOST_NAMES[stat_short]
	
	# Create the stat change entry
	stat_change = {
		"pokemon": pokemon,
		"stat": stat_full,
		event_name: change
	}
	
	# Add the stat change to the event dictionary under "stat changes"
	if "stat changes" not in event_dict:
		event_dict["stat changes"] = []
	
	event_dict["stat changes"].append(stat_change)
	
	return event_dict

def parseSource(msg: str) -> dict:
	parsed_source = msg.split("[from]")[1].split("|")[0].strip()
	source_dict = {
		"factor": parsed_source,
	}
	if "[of]" in msg:
		parsed_source_pokemon = msg.split("[of]")[1].split("|")[0].strip()
		_, pokemon = parseTrainerandPokemon(parsed_source_pokemon)
		source_dict["pokemon"] = pokemon

	return source_dict

def parseFieldStartOrEnd(msg: str) -> dict:
	# |-fieldstart|move: Electric Terrain
	# |-fieldend|move: Electric Terrain
	split_msg = msg.split('|')
	field_event_type = split_msg[1].replace('-', '') # fieldstart or fieldend
	field_name = split_msg[2].split(':')[1].strip()
	field_event_dict = {
		"field event": field_event_type,
		"field": field_name,
		"source": parseSource(msg)
	}
	return field_event_dict

def expressHPOutOf100(hp_str: str) -> str:
	if "fnt" in hp_str:
		return "0/100"
	
	hp, max_hp = hp_str.split('/')
	hp = float(hp)
	max_hp = float(max_hp)
	percent = int(math.ceil(hp / max_hp * 100))
	return str(percent) + "/100"

def parseTrainerandPokemon(msg: str):
	# Split the message to get trainer and pokemon
	# p1a: Whimsicott
	trainer_pokemon = msg.split(": ")
	trainer = trainer_pokemon[0].strip()
	pokemon = trainer_pokemon[1].strip()
	
	return trainer, pokemon

def parseOutHPString(msg: str) -> str:
	# Split the message by '|' to get all parts
	split_msg = msg.split('|')
	
	# Iterate through the parts to find the one containing the HP (which will have a "/" in it)
	for part in split_msg:
		if '/' in part:  # HP string contains a "/"
			# Further split the part by space and return the HP portion (before any status like 'par')
			return part.split()[0]  # Get only the HP part before any status condition
	
	if "fnt" in msg:
		return "0/100"

	# If no HP string found, return empty string
	return ""

def parseVolatileStatus(text: str, event_dict: dict) -> dict:
	# Split the input text based on the '|' character
	parts = text.split('|')
	
	# Check if the event is either start or end
	if len(parts) >= 4 and (parts[1] == '-start' or parts[1] == '-end'):
		# Extract the event type (start or end), target, and status
		event = 'start' if parts[1] == '-start' else 'end'
		target = parts[2].split(':')[1].strip()
		status = parts[3].strip()
		
		# Update the event_dict with the volatile status information
		event_dict["volatile status"] = {
			"event": event,
			"target": target,
			"status": status
		}
	
	return event_dict

def parseWeather(text: str, event_dict: dict) -> dict:
	# Split the message by '|'
	parts = text.split('|')

	# The weather condition is in the second part (index 2)
	weather_condition = parts[2].lower()  # Convert to lowercase for uniformity

	# https://github.com/smogon/pokemon-showdown/blob/6a1360c35b8aa5f7d54e32a492626d5298caa6f7/data/conditions.ts#L462 
	# Map the weather conditions to standard names
	weather_map = {
		"raindance": "rain",
		"primordialsea": "harsh rain",
		"sunnyday": "sun",
		"desolateland": "harsh sun",
		"sandstorm": "sandstorm",
		"hail": "hail", 
		"snow": "snow",  # Hail has been replaced by snow in later generations
		"delta stream": "delta stream",
		"none": "none"
	}

	# Assign the mapped weather condition
	event_dict["weather"] = weather_map.get(weather_condition, "none")  # Default to "none" if not found

	return event_dict

def parseAbility(text: str, event_dict: dict) -> dict:
	# Split the message by '|'
	parts = text.split('|')
	
	# Extract the trainer and Pokemon part (second part) and ability name (third part)
	trainer, pokemon = parseTrainerandPokemon(parts[2])
	ability = parts[3].strip()  # Ability name is the third part

	# Populate the event dictionary with the parsed data
	event_dict["activate ability"] = {
		"trainer": trainer,
		"pokemon": pokemon,
		"ability": ability
	}

	return event_dict

main_event_parser_lookup = {
		'move': parseUseMove,
		'switch': parseSwitchOrDrag,
		'faint': parseFaint,
		'drag': parseSwitchOrDrag,
		'detailschange': parseFormChange,
		'replace': parseFormChange,
		'cant': parseCantMove
		# 'upkeep': upkeep,
		# 'inactive': inactive,
		# 'inactiveoff': inactiveoff,
		# 'turn': turn,
		# 'noinit': noinit,
	}

subevent_parser_lookup = {
		'-heal': parseDamageOrHeal,
		'-damage': parseDamageOrHeal,
		'-boost': parseBoostUnboost,
		'-unboost': parseBoostUnboost,
		'-status': parseStatus,
		"-supereffective": parseMoveEffectiveness,
		"-resisted": parseMoveEffectiveness,
		"-immune": parseMoveEffectiveness,
		"-crit": parseCrit,
		# '-activate': activate,
		# '-prepare': prepare,
		'-start': parseVolatileStatus,
		'-end': parseVolatileStatus,
		# '-curestatus': curestatus,
		# '-cureteam': cureteam,
		# '-weather': weather,
		'-fieldstart': parseFieldStartOrEnd,
		'-fieldend': parseFieldStartOrEnd,
		# '-sidestart': sidestart,
		# '-sideend': sideend,
		# '-swapsideconditions': swapsideconditions,
		# '-item': set_item,
		# '-enditem': remove_item,
		'-ability': parseAbility,
		# '-formechange': form_change,
		# '-transform': transform,
		# '-mega': mega,
		# '-terastallize': terastallize,
		# '-zpower': zpower,
		# '-clearnegativeboost': clearnegativeboost,
		# '-clearallboost': clearallboost,
		# '-singleturn': singleturn,
}

def parse_turns_from_file(filename) -> dict[int, dict]:
	# Initialize variables
	with open(filename, 'r') as file:
		content = file.read()
	parsed_data = {}

	# Parse out just the starting turn data
	split_on_start = content.split("|start")
	if len(split_on_start) > 1:
		starting_turn = split_on_start[1].split("|turn")[0].strip().strip()
		parsed_data[0] = parseMessagesIntoEventDicts(starting_turn)

	# Split content by "|turn|" to get individual turns
	turns = content.split("|turn|")[1:]  # Skip the first empty part before the first "turn"
	for i in range(len(turns)):
		turn_data = turns[i]
		# print(turn_data)
		# Split each turn's content into lines
		turn_lines = turn_data.strip().splitlines()

		# The first line contains the turn number
		turn_number = int(turn_lines[0].strip())

		# Remaining lines are the messages we need to pass into parseMessagesIntoEventDicts
		messages = "\n".join(turn_lines[1:]).strip()
		# print("turn " + str(i))
		# print(messages + "\n")
		# Pass the extracted messages to the provided function
		event_dict = parseMessagesIntoEventDicts(messages)
		# Store the result in the dictionary using the turn number as the key
		parsed_data[turn_number] = event_dict

	return parsed_data

def parseRoomsToJoin(text) -> list[dict]:
	print("Parse rooms to join")
	print(text)

	# Split the text and isolate the JSON part
	json_text = text.split('|roomlist|')[-1]
	
	# Parse the JSON string into a Python dictionary
	data = json.loads(json_text)
	
	# Extract battle rooms from the data
	rooms = data.get("rooms", {})
	
	# Prepare the result list
	result = []
	for room_name, room_info in rooms.items():
		# For each room, extract the battle name, p1, and p2
		result.append({
			"room name": room_name,
			"p1": room_info.get("p1"),
			"p2": room_info.get("p2")
		})
	
	return result

def parse_pokemon_old(pokemon: Pokemon) -> dict:
	# note: this uses the Pokemon object from the showdown/battle.py file
	pprint.pprint(pokemon)
	parsed_dict = {
		'id': pokemon.id,
		'level': pokemon.level,
		'types': pokemon.types,
		'current_hp_percentage': (pokemon.hp / pokemon.maxhp) * 100,
		'ability': pokemon.ability,
		'item': pokemon.item,
		'attack': pokemon.stats[constants.ATTACK],
		'defense': pokemon.stats[constants.DEFENSE],
		'special-attack': pokemon.stats[constants.SPECIAL_ATTACK],
		'special-defense': pokemon.stats[constants.SPECIAL_DEFENSE],
		'speed': pokemon.stats[constants.SPEED],
		'attack_boost': pokemon.boosts[constants.ATTACK],
		'defense_boost': pokemon.boosts[constants.DEFENSE],
		'special_attack_boost': pokemon.boosts[constants.SPECIAL_ATTACK],
		'special_defense_boost': pokemon.boosts[constants.SPECIAL_DEFENSE],
		'speed_boost': pokemon.boosts[constants.SPEED],
		'accuracy_boost': pokemon.boosts[constants.ACCURACY],
		'evasion_boost': pokemon.boosts[constants.EVASION],
		'status': pokemon.status,
		'terastallized': pokemon.terastallized,
		'volatileStatus': pokemon.volatile_statuses,
		'moves': [move[constants.ID] for move in pokemon.moves]
	}
	return parsed_dict

def parse_pokemon(pokemon: TransposePokemon) -> dict:
    # Create a dictionary representing the key attributes of the TransposePokemon instance
    parsed_dict = {
        'id': pokemon.id,
        'level': pokemon.level,
        'types': pokemon.types,
        'current_hp_percentage': (pokemon.hp / pokemon.maxhp) * 100,
        'ability': pokemon.ability,
        'item': pokemon.item,
        'attack': pokemon.attack,
        'defense': pokemon.defense,
        'special-attack': pokemon.special_attack,
        'special-defense': pokemon.special_defense,
        'speed': pokemon.speed,
        'attack_boost': pokemon.attack_boost,
        'defense_boost': pokemon.defense_boost,
        'special_attack_boost': pokemon.special_attack_boost,
        'special_defense_boost': pokemon.special_defense_boost,
        'speed_boost': pokemon.speed_boost,
        'accuracy_boost': pokemon.accuracy_boost,
        'evasion_boost': pokemon.evasion_boost,
        'status': pokemon.status,
        'terastallized': pokemon.terastallized,
        'volatileStatus': list(pokemon.volatile_status),
        'moves': pokemon.moves
    }
    return parsed_dict

def parse_side(side: Side) -> dict:
	parsed_dict = {
		"active": parse_pokemon(side.active),
		"reserve": [parse_pokemon(pokemon) for pokemon in side.reserve.values()],
		"wish active": side.wish, 
		"side conditions": side.side_conditions,
		"future sight active": side.future_sight
	}
	return parsed_dict

def parse_state(state: State) -> dict[str, any]:
    return {
        "self": parse_side(state.user),
        "opponent": parse_side(state.opponent),
        constants.WEATHER: state.weather,
        constants.FIELD: state.field,
        constants.TRICK_ROOM: state.trick_room
    }

def parse_move_data(move_info: dict[str, any]) -> dict[str, any]:
    attributes_to_copy = ['id', 'accuracy', 'basePower', 'category', 'priority', 'target', 'type']
    
    parsed_move_data = {attr: move_info[attr] for attr in attributes_to_copy if attr in move_info}
    parsed_move_data['name'] = parsed_move_data.pop('id').lower()

    # Add boosts if present
    if 'boosts' in move_info:
        parsed_move_data['boosts'] = move_info['boosts']

    # Add status condition if present
    if 'status' in move_info:
        parsed_move_data['status'] = move_info['status']
    
    return parsed_move_data

import re 

def chunk_message_smartly(max_message_size: int, message: str) -> list[str]:
	"""
	Chunks message into logical parts based on sentence boundaries. Will try to get each chunk as close to max_message_size as possible.
	"""
	# Handle non-positive message size limit
	if max_message_size <= 0:
		raise ValueError("max_message_size must be greater than zero")

	# Handle empty message
	if not message:
		return []

	# Split message at sentence boundaries (period, question mark, exclamation mark, etc.)
	sentences = re.split(r'(?<=[.!?])\s+', message.strip())
	
	chunks = []
	current_chunk = ""

	for sentence in sentences:
		# If adding the current sentence would exceed the max message size
		if len(current_chunk) + len(sentence) + 1 > max_message_size:  # +1 accounts for the space
			# If current chunk is not empty, append it to chunks
			if current_chunk:
				chunks.append(current_chunk.strip())
			current_chunk = sentence  # Start a new chunk with the current sentence
		else:
			# Add the sentence to the current chunk
			if current_chunk:
				current_chunk += " " + sentence
			else:
				current_chunk = sentence

	# Append any remaining chunk
	if current_chunk:
		chunks.append(current_chunk.strip())
	
	return chunks