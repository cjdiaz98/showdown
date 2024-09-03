from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate, SystemMessagePromptTemplate
import constants
from showdown.engine.objects import Pokemon
from showdown.battle_bots.helpers import count_fainted_pokemon_in_reserve
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

BATTLE_SYSTEM_INSTRUCTIONS = """I will give you the following information:
Your possible choices for the turn. 
Your pokemon's moves and their projected damages. 
Your opponent's active pokemon. 
Your opponent's known reserve pokemon.

To designate your choice, put\n
CHOICE:
'<Option>'
END
Where <Option> is one of the following:
If you choose to use a move, output:
move <MOVE NAME>.
If you choose to switch pokemon, output:
switch <POKEMON TO SWITCH>.""" # To do 

TERA_SYSTEM_INSTRUCTIONS = """If you choose a move and want to terastallize your pokemon the same turn. Put the following under CHOICE:
terastallize <TERA TYPE>
This is only possible when your current pokemon can terastallize."""

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

MOVE_DAMAGES_PROMPT_TEMPLATE = "Your pokemon's moves, and their projected damages are: {moves_and_damages}"

OPPONENT_INFORMATION_PROMPT_TEMPLATE = """Your opponent's active pokemon is: {opponent_pokemon}. Their known choice options are {opponent_options}.\n
Your opponent has {num_opp_reserve} reserve pokemon. Of those, the following are known: {opponent_known_reserve}"""

def create_combined_prompt_template():
	# Combine all templates into one big template
	combined_template = "\n".join([
		BATTLE_SYSTEM_INSTRUCTIONS,
		TERA_SYSTEM_INSTRUCTIONS,
		"BATTLE CONTEXT:",
		USER_ACTIVE_PROMPT_TEMPLATE,
		USER_OPTIONS_PROMPT_TEMPLATE,
		USER_RESERVE_PROMPT_TEMPLATE,
		MOVE_DAMAGES_PROMPT_TEMPLATE,
		OPPONENT_INFORMATION_PROMPT_TEMPLATE
	])
	
	# Create a PromptTemplate from the combined template
	return PromptTemplate.from_template(combined_template)

def generate_prompt_with_context(battle: Battle) -> str:
	state = battle.create_state()
	my_options, opponent_options = battle.get_all_options()
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
	
	opponent_known_reserve = []
	opponent_active = None

	if "opponent" in parsed_state:
		opponent_active = parsed_state["opponent"].get("active")

		reserve = parsed_state["opponent"].get("reserve")
		if reserve:
			opponent_known_reserve = reserve

	# Create the combined prompt template
	combined_prompt_template = create_combined_prompt_template()
	
	# Format the template with the extracted arguments
	formatted_prompt = combined_prompt_template.format(
		user_active=trainer_active,
		user_options=my_options,
		moves_and_damages=move_damages,
		user_reserve=trainer_reserve,
		opponent_pokemon=opponent_active,
		opponent_options=opponent_options,
		num_opp_reserve=opponent_reserve_size,
		opponent_known_reserve=opponent_known_reserve
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

def parse_llm_output(llm_output: str) -> list[str]:
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
