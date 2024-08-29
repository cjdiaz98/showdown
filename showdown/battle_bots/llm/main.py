import constants
from data import all_move_json
from showdown.battle import Battle
from showdown.engine.damage_calculator import calculate_damage
from showdown.engine.find_state_instructions import update_attacking_move
from ..helpers import format_decision, get_battle_conditions
from showdown.engine.damage_calculator import _calculate_damage
from showdown.battle import Pokemon, Side, State

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

BATTLE_PROMPT = "" # To do 
BOT_PERSONALITY = "" # TO DO: list different personalities the bot can assume
TERA_EXPLANATION = """When a Pokémon Terastallizes, it changes its type to its Tera Type, which could be the same as one of its current types or completely different.
This transformation boosts the power of moves that match the new Tera Type and can give strategic advantages in battles.
Terastallizing lasts until the battle ends, and only one pokemon can terastallize per battle.
This allows for flexibility in type matchups and can be used offensively or defensively depending on the situation."""
MOVE_MOST_DAMAGE = "The move projected to do the most damage is: {}"

class BattleBot(Battle):
	def __init__(self, *args, **kwargs):
		super(BattleBot, self).__init__(*args, **kwargs)

	def find_best_move(self):
		state = self.create_state()
		opponent_pokemon = state.opponent.active
		user_pokemon = state.user.active
		opponent_reserve = state.opponent.reserve
		user_reserve = state.user.reserve

		# terrain = state. # not implemented in base code
		my_options, opponent_options = self.get_all_options()[0]
		move_damages = self.get_move_damages()
		
		# to do: if pokemon is choiced, we have to pick only one move
		# to do: get weaknesses of opponent and our pokemon 
		# to do: get opponent speed range and compare to ours
		moves = [] # to do: get move accuracy, power, and type
		# to do: get move priority
		# to do: implement bots monologuing to their opponent. Then we can actually implement bots that talk back to the opponent

		switches = []

		if self.force_switch or not moves:
			return format_decision(self, switches[0])

		return format_decision(self, choice)

	def get_all_switch_options(self):
		return [action for action in self.get_all_options() if action.startswith(constants.SWITCH_STRING + " ")]
	
	def get_additional_context_for_prompt(self):
		# to do: depending on certain conditions (e.g. whether the user can tera, whether the user can dynamax, whether the user can z-move, etc.), we'll give different context to the bot
		# if user can tera still
		# if weather is active
		# if terrain is active
		pass

	def handle_win(self):
		# to do: implement a win behavior. Gloating or being humble or salty
		pass

	def get_move_damages(self) -> dict[str, float]:
		attacker: Pokemon = self.user.active
		opponent: Pokemon = self.opponent.active
		move_damages = dict()
		conditions = get_battle_conditions(self, self.opponent)
		for move in attacker.moves:
			move_damage = _calculate_damage(attacker, opponent, move, conditions)
			move_damages[move] = move_damage






