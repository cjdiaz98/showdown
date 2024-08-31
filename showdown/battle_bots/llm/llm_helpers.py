from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate
import constants
from showdown.battle_bots.helpers import count_fainted_pokemon_in_reserve

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
'<Option>'\n
Where <Option> is one of the following:
If you choose to use a move, output:
move <MOVE NAME>.
If you choose to switch pokemon, output:
switch <POKEMON TO SWITCH>.""" # To do 
TERA_SYSTEM_INSTRUCTIONS = """If your current pokemon can terastallize, and you want to do that you can output:\n
terastallize <TERA TYPE>"""

# note: Add the below when you want to give the bot dialogue options
"""In addition to which choice you want to make, you will also provide some dialogue commentating on the battle and why you made the choice you did."""

BOT_PERSONALITY = "" # TO DO: list different personalities the bot can assume
TERA_EXPLANATION = """When a Pokémon Terastallizes, it changes its type to its Tera Type, which could be the same as one of its current types or completely different.
This transformation boosts the power of moves that match the new Tera Type and can give strategic advantages in battles.
Terastallizing lasts until the battle ends, and only one pokemon can terastallize per battle.
This allows for flexibility in type matchups and can be used offensively or defensively depending on the situation."""

MOVE_MOST_DAMAGE = "The move projected to do the most damage is: {move_name}"

USER_RESERVE_PROMPT = "Your reserve pokemon are: {user_reserve}"
USER_OPTIONS_PROMPT = "Your options are: {user_options}"

MOVE_DAMAGES_PROMPT = "Your pokemon's moves, and their projected damages are: {moves_and_damages}"

OPPONENT_INFORMATION_PROMPT = """Your opponent's active pokemon is: {opponent_pokemon}. Their known choice options are {opponent_options}.\n
Your opponent has {num_opp_reserve} reserve pokemon. Of those, the following are known: {opponent_known_reserve}"""

def format_prompt(user_options: list[str], opponent_options: list[str], move_damages: dict[str, float], parsed_state: dict[str, any]) -> str:
	""""""
	chat_template = ChatPromptTemplate.from_messages(
		[
			SystemMessage(
				content=(
					[BATTLE_SYSTEM_INSTRUCTIONS, TERA_SYSTEM_INSTRUCTIONS]
				)
			),
			HumanMessagePromptTemplate.from_template(USER_OPTIONS_PROMPT),
			HumanMessagePromptTemplate.from_template(MOVE_DAMAGES_PROMPT),
			HumanMessagePromptTemplate.from_template(USER_RESERVE_PROMPT),
			HumanMessagePromptTemplate.from_template(OPPONENT_INFORMATION_PROMPT),
		]
	)

	if not user_options:
		print("no user options")
		return None
	
	trainer_reserve = []
	trainer_active = None
	
	if constants.SELF in parsed_state:
		trainer_active = parsed_state[constants.SELF].get("active")
		trainer_reserve = parsed_state[constants.SELF].get("reserve")
		
	if not trainer_active:
		print("no trainer active")
		return None # If we are somehow missing the user context there's really not much we can do
	
	num_opp_reserve = constants.RANBATS_NUMBER_OF_SLOTS - 1 # to do: change to account for different battle type

	opponent_known_reserve = []
	opponent_active = None

	if "opponent" in parsed_state:
		opponent_active = parsed_state["opponent"].get("active")

		reserve = parsed_state["opponent"].get("reserve")
		num_opp_reserve -= count_fainted_pokemon_in_reserve(reserve)
		if reserve:
			opponent_known_reserve = reserve

	return chat_template.format(user_options=user_options,
							 moves_and_damages=move_damages,
							 user_reserve = trainer_reserve,
							 opponent_pokemon=opponent_active,
							 opponent_options=opponent_options,
							 num_opp_reserve=num_opp_reserve,
							 opponent_known_reserve=opponent_known_reserve)

import re

def parse_llm_output2(llm_output: str):
	"""
	Parses the LLM output to extract valid move, switch, and terastallize commands, removing any single quotes.
	
	Args:
		llm_output (str): The output from the LLM.

	Returns:
		str: The parsed commands if valid, otherwise None.
	"""
	# Use a regular expression to find all valid commands within the first "CHOICE:" block
	matches = re.findall(r"CHOICE:\s*'(.*?)'", llm_output, re.IGNORECASE | re.DOTALL)

	# Filter out and process the captured commands
	commands = []
	for match in matches:
		command = match.strip()
		if command.startswith("move") and len(command.split()) > 1:
			commands.append(command)
		elif command.startswith("switch") and len(command.split()) > 1:
			commands.append(command)
		elif command.startswith("terastallize") and len(command.split()) > 1:
			commands.append(command)

	# Return the commands joined by newlines, or None if no valid commands were found
	return "\n".join(commands) if commands else None

import re

def parse_llm_output(llm_output: str) -> list[str]:
	"""
	Parses the LLM output to extract a valid move or switch command, optionally including terastallize if there is a move command.
	
	Args:
		llm_output (str): The output from the LLM.

	Returns:
		str: The parsed command(s) if valid, otherwise None.
	"""
	# Use regular expressions to match the commands
	move_match = re.search(r"CHOICE:\s*'move\s+\w+(?:\s+\w+)*'", llm_output, re.IGNORECASE)
	switch_match = re.search(r"CHOICE:\s*'switch\s+\w+(?:\s+\w+)*'", llm_output, re.IGNORECASE)
	tera_match = re.search(r"\s*'terastallize\s+\w+(?:\s+\w+)*'", llm_output, re.IGNORECASE)

	# If neither move nor switch command is found, return None (invalid)
	if not move_match and not switch_match:
		return None

	commands = []
	
	# If a move command is found, add it to the result
	if move_match:
		move_command = move_match.group(0).split("'")[1].strip()
		commands.append(move_command)
		
		# If a terastallize command is also found, add it to the result
		if tera_match:
			tera_command = tera_match.group(0).split("'")[1].strip()
			commands.append(tera_command)
	
	# If only a switch command is found, add it to the result
	elif switch_match:
		switch_command = switch_match.group(0).split("'")[1].strip()
		commands.append(switch_command)

	# Return the commands joined by newlines, or None if no valid commands were found
	return commands if commands else None
