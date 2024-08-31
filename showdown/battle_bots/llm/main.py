import constants
from data import all_move_json
from showdown.battle import Battle, State
from showdown.engine.damage_calculator import calculate_damage
from showdown.engine.find_state_instructions import update_attacking_move
from ..helpers import format_decision, get_battle_conditions
from showdown.engine.damage_calculator import _calculate_damage
from showdown.engine.objects import Pokemon
from showdown.Commentary.parsingUtils import parse_pokemon, parse_side, parse_state, parse_move_data
from pprint import pprint
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAI
from config import ShowdownConfig
from showdown.battle_bots.llm.llm_helpers import format_prompt

class BattleBot(Battle):
	def __init__(self, *args, **kwargs):
		super(BattleBot, self).__init__(*args, **kwargs)
		self.llm = OpenAI(
				model="gpt-4o",
				temperature=0,
				max_retries=2,
				api_key=ShowdownConfig.open_ai_key,
			)

	def find_best_move(self):
		state = self.create_state()
		# pprint(state.user.reserve)
		state_parsed = parse_state(state)
		opponent_pokemon = state.opponent.active
		user_pokemon = state.user.active
		opponent_reserve = state.opponent.reserve
		user_reserve = state.user.reserve

		# terrain = state. # not implemented in base code
		my_options, opponent_options = self.get_all_options()
		print("my options: ", my_options)
		print("opponent options: ", opponent_options)

		move_damages = self.get_move_damages(state)
		print("move damages: ", move_damages)
		pprint("state_parsed: " + str(state_parsed))
		# to do: if pokemon is choiced, we have to pick only one move
		# to do: get weaknesses of opponent and our pokemon 
		# to do: get opponent speed range and compare to ours
		moves = [] # to do: get move accuracy, power, and type
		# to do: get move priority
		# to do: implement bots monologuing to their opponent. Then we can actually implement bots that talk back to the opponent
		prompt = format_prompt(my_options, opponent_options, move_damages, state_parsed)

		# if self.force_switch or not moves:
			# return format_decision(self, switches[0])
		return None
		# return format_decision(self, choice)

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

	def get_move_damages(self, state: State) -> dict[str, float]:
		attacker: Pokemon = state.user.active
		opponent: Pokemon = state.opponent.active
		move_damages = dict()
		conditions = get_battle_conditions(self, state.opponent)
		for move in attacker.moves:
			move_name = move[constants.ID]
			move_damage = _calculate_damage(attacker, opponent, move_name, conditions)
			move_damages[move_name] = move_damage
			if move_damage and len(move_damage) > 1:
				move_damages[move_name] = move_damage[0] # just get a single number
		return move_damages






