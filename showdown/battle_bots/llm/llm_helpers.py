from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate

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

If you choose to use a move, you must output:\n
move <MOVE NAME>.
If you choose to switch pokemon, output:\n
switch <POKEMON TO SWITCH>.""" # To do 
TERA_SYSTEM_INSTRUCTIONS = """If your current pokemon can terastallize, and you want to do that you can output:\n
terastallize <POKEMON NAME>"""

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
		return None
	
	trainer_reserve = []
	trainer_active = None

	if "user" in parsed_state:
		trainer_active = parsed_state["user"].get("active")
		trainer_reserve = parsed_state["user"].get("reserve")
		
	if not trainer_active:
		return None # If we are somehow missing the user context there's really not much we can do
	
	num_opp_reserve = 0
	opponent_known_reserve = []
	opponent_active = None

	if "opponent" in parsed_state:
		opponent_active = parsed_state["opponent"].get("active")

		reserve = parsed_state["opponent"].get("reserve")
		if reserve:
			num_opp_reserve = len(reserve)
			opponent_known_reserve = reserve

	return chat_template.format(user_options=user_options,
							 moves_and_damages=move_damages,
							 user_reserve = trainer_reserve,
							 opponent_pokemon=opponent_active,
							 opponent_options=opponent_options,
							 num_opp_reserve=num_opp_reserve,
							 opponent_known_reserve=opponent_known_reserve)

def parse_decision(llm_output: str):
	# to do: parse the decision from the LLM output
	return llm_output