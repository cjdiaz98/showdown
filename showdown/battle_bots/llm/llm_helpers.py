from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate, SystemMessagePromptTemplate
import constants
from showdown.engine.objects import Pokemon
from showdown.battle_bots.helpers import count_fainted_pokemon_in_reserve, get_non_fainted_pokemon_in_reserve
from showdown.Commentary.parsingUtils import parse_state
from showdown.battle import Battle, State
from ..helpers import get_battle_conditions
from showdown.engine.damage_calculator import _calculate_damage#, calculate_damage

"""
FUTURE BOT IMPROVEMENTS:
- implement memory of the user's playstyle and use it to make decisions
- implement a bot that will attempt reads on the opponent
- account for the current pokemon being trapped
- incentivize it to use hazards and status moves if advantageous
- incentivize to setup if advantageous (e.g. start dragon dancing)
- take into account other conditions (e.g. weather, terrain, etc.)
- trick room
- stat matchups. E.g. more likely to switch a physical wall into a physical attacker (we can use pokedex for this)
- miscellaneous considerations (e.g. not being able to use prankster moves on dark types)
"""

POSSIBLE_ACTIONS = [
	"move",
	"switch",
]

######## SYSTEM INSTRUCTIONS ########
BOT_PERSONA = """You are a passionate and highly skilled pokemon trainer engaged in a battle with a worthy opponent.
You are tasked with making decisions to win the battle, and talking to your opponent along the way."""

BATTLE_SYSTEM_INSTRUCTIONS = """To make your battle decisions you'll get the following information:
Your possible choices for the turn. 
Your pokemon's moves and their projected damages. 
Your opponent's active pokemon. 
Your opponent's known reserve pokemon.

Reason concisely and logically about what the best move would be given the information you know.
To designate your choice, put\n
CHOICE:
'<Option>'
END
Where <Option> is one of the following:
If you choose to use a move, output:
move <MOVE NAME>.
If you choose to switch pokemon, output:
switch <POKEMON TO SWITCH>.

As for strategy, please keep in mind that switching in another pokemon Will burn a turn and allow for the opponent to attack the incoming Pokemon or set up some condition that is favorable to them.
Switching should only be done when it is expected that the switch will highly be in your favor, such as when the opponent can't do much damage to the incoming pokemon.
For moves, even if a move doesn't damage the opponent, it could very well be worth using if it'll give you an advantage in the coming turns. There should be a good balance between setup and offense.
"""

TERA_SYSTEM_INSTRUCTIONS = """If you choose a move and want to terastallize your pokemon the same turn. Put the following under CHOICE:
terastallize <TERA TYPE>
This is only possible when your current pokemon can terastallize."""

BATTLE_COMMENTARY_INSTRUCTIONS = """You are to generate commentary from the perspective of a Pokémon trainer, reflecting on a heated battle. 
Your commentary should be dramatic, filled with taunts, and reflect the emotions of a competitive Pokémon battle. It is important to be concise.
When generating responses, follow this format:
COMMENTARY:
<put commentary here>
END"""

######## BOT CONTEXT ########
# note: Add the below when you want to give the bot dialogue options
"""In addition to which choice you want to make, you will also provide some dialogue commentating on the battle and why you made the choice you did."""

BOT_PERSONALITY = "" # TO DO: list different personalities the bot can assume
TERA_EXPLANATION = """When a Pokémon Terastallizes, it changes its type to its Tera Type, which could be the same as one of its current types or completely different.
This transformation boosts the power of moves that match the new Tera Type and can give strategic advantages in battles.
Terastallizing lasts until the battle ends, and only one pokemon can terastallize per battle.
This allows for flexibility in type matchups and can be used offensively or defensively depending on the situation."""

MOVE_MOST_DAMAGE = "The move projected to do the most damage is: {move_name}"

USER_ACTIVE_PROMPT_TEMPLATE = "Your current active pokemon is: {user_active}"
USER_RESERVE_PROMPT_TEMPLATE = "Your reserve pokemon are: {user_reserve}"
USER_OPTIONS_PROMPT_TEMPLATE = "Your options are: {user_options}"
LAST_MOVES_PROMPT_TEMPLATE = "Your last move was: {user_last_move}. Opponent's last move was: {opponent_last_move}"

MOVE_DAMAGES_PROMPT_TEMPLATE = "Your pokemon's moves, and their projected damages are: {moves_and_damages}"
TYPE_WEAKNESSES_PROMPT_TEMPLATE = "Your pokemon's type weaknesses are: {type_weaknesses}"
TYPE_RESISTANCES_PROMPT_TEMPLATE = "Your pokemon's type resistances are: {type_resistances}"

OPPONENT_WEAKNESSES_PROMPT_TEMPLATE = "The opponent's pokemon's type weaknesses are: {opponent_type_weaknesses}"
OPPONENT_RESISTANCES_PROMPT_TEMPLATE = "The opponent's pokemon's type resistances are: {opponent_type_resistances}"

OPPONENT_INFORMATION_PROMPT_TEMPLATE = """Your opponent's active pokemon is: {opponent_pokemon}. Their known choice options are {opponent_options}.\n
Your opponent has {num_opp_reserve} reserve pokemon. Of those, the following are known: {opponent_known_reserve}"""

OPPONENT_NUM_KNOWN_MOVES_TEMPLATE = """{num_known_opponent_moves} out of 4 of your opponent's moves are known."""

OUTSPEED_OPP_TEMPLATE = """Our current pokemon outspeeds the opponent's pokemon: {do_we_outspeed_opponent}"""

def create_combined_prompt_template():
	# Combine all templates into one big template
	combined_template = "\n".join([
		BOT_PERSONA,
		BATTLE_SYSTEM_INSTRUCTIONS,
		TERA_SYSTEM_INSTRUCTIONS,
		BATTLE_COMMENTARY_INSTRUCTIONS,
		"\nBATTLE CONTEXT:",
		USER_ACTIVE_PROMPT_TEMPLATE,
		USER_OPTIONS_PROMPT_TEMPLATE,
		TYPE_WEAKNESSES_PROMPT_TEMPLATE,
		TYPE_RESISTANCES_PROMPT_TEMPLATE,
		USER_RESERVE_PROMPT_TEMPLATE,
		MOVE_DAMAGES_PROMPT_TEMPLATE,
		OPPONENT_INFORMATION_PROMPT_TEMPLATE,
		OPPONENT_WEAKNESSES_PROMPT_TEMPLATE,
		OPPONENT_RESISTANCES_PROMPT_TEMPLATE,
		OPPONENT_NUM_KNOWN_MOVES_TEMPLATE,
		LAST_MOVES_PROMPT_TEMPLATE,
		OUTSPEED_OPP_TEMPLATE
	])
	
	# Create a PromptTemplate from the combined template
	return PromptTemplate.from_template(combined_template)

def generate_prompt_with_context(battle: Battle) -> str:
	state = battle.create_state()
	battle.user.lock_moves()
	battle.opponent.lock_moves()
	my_options, opponent_options = battle.get_all_options()
	if "splash" in opponent_options:
		opponent_options.remove("splash") # remove to not throw off the LLM

	# print("my options: ", my_options)
	# print("opponent options: ", opponent_options)

	move_damages = get_move_damages(battle,state) # to do: get move accuracy and priority too
	# print("move damages: ", move_damages)
	# pprint("state_parsed: " + str(state_parsed))
	# to do: if pokemon is choiced, we have to pick only one move
	# to do: get opponent speed range and compare to ours
	opponent_reserve_size = constants.RANBATS_NUMBER_OF_SLOTS - 1 - count_fainted_pokemon_in_reserve(state.opponent.reserve)

	if not my_options:
		print("no user options")
		return None
	
	trainer_reserve = []
	trainer_active = None

	parsed_state = parse_state(state)
	
	if constants.SELF in parsed_state:
		trainer_active = parsed_state[constants.SELF].get("active")
		trainer_reserve = parsed_state[constants.SELF].get("reserve")
		
	if not trainer_active:
		print("no trainer active")
		return None # If we are somehow missing the user context there's really not much we can do
	
	trainer_type_resistances = get_pokemon_resistances(battle.user.active)
	trainer_type_weaknesses = get_pokemon_weaknesses(battle.user.active)
	if battle.user.last_used_move:
		trainer_last_move_str = battle.user.last_used_move.move
	else:
		trainer_last_move_str = "None"

	opponent_known_reserve = []
	opponent_active = None

	if "opponent" in parsed_state:
		opponent_active = parsed_state["opponent"].get("active")

		reserve = parsed_state["opponent"].get("reserve")
		if reserve:
			opponent_known_reserve = reserve
	opponent_weaknesses = get_pokemon_weaknesses(battle.opponent.active)
	opponent_resistances = get_pokemon_resistances(battle.opponent.active)
	num_known_opponent_moves = len(list(filter(lambda option: not option.startswith("switch"), opponent_options)))
	if battle.opponent.last_used_move:
		opp_last_move_str = battle.opponent.last_used_move.move
	else:
		opp_last_move_str = "None"

	do_we_outspeed = pokemon_outspeeds_opponent(battle.user.active, battle.opponent.active)
	values = [
		trainer_active,
		my_options,
		trainer_type_resistances,
		trainer_type_weaknesses,
		move_damages,
		trainer_reserve,
		opponent_active,
		opponent_options,
		num_known_opponent_moves,
		opponent_reserve_size,
		opponent_known_reserve,
		opponent_weaknesses,
		opponent_resistances,
		battle.user.last_used_move.move,
		battle.opponent.last_used_move.move,
		do_we_outspeed
	]

	# Assert that none of the values are None
	assert all(value is not None for value in values), "One or more values passed to format are None"

	# Create the combined prompt template
	combined_prompt_template = create_combined_prompt_template()

	# Format the template with the extracted arguments
	formatted_prompt = combined_prompt_template.format(
		user_active=trainer_active,
		type_resistances=str(trainer_type_resistances),
		type_weaknesses=str(trainer_type_weaknesses),
		user_options=my_options,
		moves_and_damages=move_damages,
		user_reserve=trainer_reserve,
		opponent_pokemon=opponent_active,
		opponent_options=opponent_options,
		num_known_opponent_moves = num_known_opponent_moves,
		num_opp_reserve=opponent_reserve_size,
		opponent_known_reserve=opponent_known_reserve,
		opponent_type_weaknesses=str(opponent_weaknesses),
		opponent_type_resistances=opponent_resistances,
		user_last_move=trainer_last_move_str,
		opponent_last_move=opp_last_move_str,
		do_we_outspeed_opponent=do_we_outspeed
	)
	
	return formatted_prompt

def get_move_damages(battle: Battle, state: State) -> dict[str, float]:
	attacker: Pokemon = state.user.active
	opponent: Pokemon = state.opponent.active
	move_damages = dict()
	conditions = get_battle_conditions(battle, state.opponent)

	for move in attacker.moves:
		move_name = move[constants.ID]
		move_damage = _calculate_damage(attacker, opponent, move_name, conditions)
		move_damages[move_name] = move_damage
		if move_damage and len(move_damage) >= 1:
			move_damages[move_name] = move_damage[0] # just get a single number
		
	return move_damages

from showdown.battle_bots.type_matchup_helper import get_matchups

def get_pokemon_weaknesses(pokemon: Pokemon) -> set[str]:
	types = pokemon.types
	matchups = get_matchups(types)
	weaknesses = set()
	for type in matchups:
		if matchups[type] > 1:
			weaknesses.add(type)

	return weaknesses

def get_pokemon_resistances(pokemon: Pokemon) -> set[str]:
	types = pokemon.types
	matchups = get_matchups(types)
	resistances = set()
	for type in matchups:
		if matchups[type] < 1:
			resistances.add(type)

	return resistances 

def pokemon_outspeeds_opponent(pokemonA: Pokemon, opposingPokemon: Pokemon) -> str:
	print("Speed range:" + str(opposingPokemon.speed_range))
	print("Stats:" + str(pokemonA.stats))
	
	if not opposingPokemon.speed_range or not pokemonA.stats or not pokemonA.stats.get(constants.SPEED):
		return "Maybe"
	
	our_speed = pokemonA.stats.get(constants.SPEED)
	# to do: see team_datasets.py:speed_check method
	if our_speed < opposingPokemon.speed_range.min:
		return "No"
	elif our_speed <= opposingPokemon.speed_range.max:
		return "Maybe"
	else:
		return "Yes"

import re

def parse_llm_output2(llm_output: str) -> list[str]:
	"""
	Parses the LLM output to extract valid move or switch commands, optionally including terastallize if there is a move command.
	
	Args:
		llm_output (str): The output from the LLM.

	Returns:
		list[str]: The parsed command(s) if valid, otherwise None.
	"""
	# Define patterns to find commands
	move_pattern = r"CHOICE:\s*move\s+\w+(?:\s+\w+)*"
	switch_pattern = r"CHOICE:\s*switch\s+\w+(?:\s+\w+)*"
	tera_pattern = r"terastallize\s+\w+(?:\s+\w+)*"
	
	# Extract the relevant portion of the output
	choice_section = re.search(r"CHOICE:.*?END", llm_output, re.DOTALL)
	
	if choice_section:
		choice_text = choice_section.group(0)
		
		# Extract move and switch commands
		move_match = re.search(move_pattern, choice_text, re.IGNORECASE)
		switch_match = re.search(switch_pattern, choice_text, re.IGNORECASE)
		tera_match = re.search(tera_pattern, llm_output, re.IGNORECASE)
		
		commands = []
		if move_match:
			move_command = move_match.group(0).replace("CHOICE:", "").strip()
			commands.append(move_command)

			# Check for a terastallize command if a move command is present
			if tera_match:
				tera_command = tera_match.group(0).strip()
				commands.append(tera_command)
		
		elif switch_match:
			# Extract switch command and ignore anything after the first newline
			switch_command = switch_match.group(0).replace("CHOICE:", "").strip()
			switch_command = re.sub(r'\s*\n.*$', '', switch_command)  # Remove everything after the first newline
			commands.append(switch_command)
		
		return commands if commands else None
	
	return None

def parse_choice_from_llm_output(llm_output: str) -> list[str]:
	"""
	Parses the LLM output to extract valid move or switch commands, optionally including terastallize if there is a move command.
	
	Args:
		llm_output (str): The output from the LLM.

	Returns:
		list[str]: The parsed command(s) if valid, otherwise None.
	"""
	# Define patterns to find commands
	move_pattern = r"move (?:\S+(?: \S+)*)"
	switch_pattern = r"switch (?:\S+(?: \S+)*)"
	terastallize_pattern = r"terastallize \S+"
	
	# Extract the relevant portion of the output
	choice_section = re.search(r"CHOICE:.*?END", llm_output, re.DOTALL)
	
	if choice_section:
		choice_text = choice_section.group(0)
		choice_text = choice_text.replace("CHOICE:", "").strip()
		choice_text = choice_text.replace("END", "").strip()
		
		# Extract move and switch commands
		move_match = re.search(move_pattern, choice_text, re.IGNORECASE)
		switch_match = re.search(switch_pattern, choice_text, re.IGNORECASE)
		tera_match = re.search(terastallize_pattern, llm_output, re.IGNORECASE)
		
		commands = []
		if move_match:
			move_command_split = move_match.group(0).split('\n')
			if len(move_command_split) > 0:
				commands.append(move_command_split[0].replace("move", "").strip())

			# Check for a terastallize command if a move command is present
			if tera_match:
				tera_command = tera_match.group(0).strip()
				commands.append(tera_command)
		
		elif switch_match:
			switch_command = switch_match.group(0)
			switch_command = re.sub(r'\s*\n.*$', '', switch_command)  # Remove everything after the first newline
			commands.append(switch_command)
		
		return commands if commands else None
	
	return None

def parse_commentary_from_llm_output(llm_output: str) -> str:
	"""
	Parses the LLM output to extract any bot commentary.
	
	Args:
		llm_output (str): The output from the LLM.

	Returns:
		str: The parsed commentary if valid, otherwise an empty string.
	"""
	# Split the content based on COMMENTARY marker
	commentary_marker = "COMMENTARY:"
	end_marker = "END"

	# Find the section that begins with COMMENTARY
	commentary_start = llm_output.find(commentary_marker)
	
	# If COMMENTARY is not found, return an empty string
	if commentary_start == -1:
		return ""

	# Slice from the point after "COMMENTARY:" marker
	commentary_start += len(commentary_marker)

	# Find the end of the commentary section
	commentary_end = llm_output.find(end_marker, commentary_start)
	
	# If END is not found after COMMENTARY, return an empty string
	if commentary_end == -1:
		return ""
	
	# Extract and clean the commentary (strip leading/trailing spaces and newlines)
	commentary = llm_output[commentary_start:commentary_end]
	commentary = commentary.replace("CHOICE:", "") # replace any other tags that we don't want to display
	commentary = commentary.strip()

	return commentary
