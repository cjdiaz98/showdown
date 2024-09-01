import constants
from data import all_move_json
from showdown.battle import Battle, State
from showdown.engine.damage_calculator import calculate_damage
from showdown.engine.find_state_instructions import update_attacking_move
from ..helpers import format_decision, get_battle_conditions
from showdown.engine.damage_calculator import _calculate_damage
from showdown.engine.objects import Pokemon
from showdown.Commentary.parsingUtils import parse_state
from pprint import pprint
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAI
from config import ShowdownConfig
from showdown.battle_bots.llm.llm_helpers import format_prompt, parse_llm_output
from showdown.battle_bots.helpers import count_fainted_pokemon_in_reserve

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
		prompt = self.get_prompt_with_battle_context()
		print("PROMPT \n" + prompt)
		llm_response = self.llm.invoke(prompt)
		print("RESPONSE \n" + llm_response)
		parse_output = parse_llm_output(llm_response)
		# to do: See if we want to list a stop sequence such as "END"

		if not parse_output:
			return None
		
		# if self.force_switch or not moves: # How do we handle a forced switch?
		decision = format_decision(self, parse_output[0])

		if len(parse_output) > 1 and not constants.TERASTALLIZE in parse_output[0] and parse_output[1].lower().startsWith(constants.TERASTALLIZE):
			# format decision to have tera if the LLM decided it and not already present
			decision[0] = decision[0] + " " + constants.TERASTALLIZE

		return decision

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
			if move_damage and len(move_damage) >= 1:
				move_damages[move_name] = move_damage[0] # just get a single number
			
		return move_damages

	def get_prompt_with_battle_context(self) -> str:
		state = self.create_state()
		state_parsed = parse_state(state)

		my_options, opponent_options = self.get_all_options()
		# print("my options: ", my_options)
		# print("opponent options: ", opponent_options)

		move_damages = self.get_move_damages(state) # to do: get move accuracy and priority too
		# print("move damages: ", move_damages)
		# pprint("state_parsed: " + str(state_parsed))
		# to do: if pokemon is choiced, we have to pick only one move
		# to do: get opponent speed range and compare to ours
		opponent_reserve_size = constants.RANBATS_NUMBER_OF_SLOTS - 1 - count_fainted_pokemon_in_reserve(state.opponent.reserve)
		# to do: implement bots monologuing to their opponent. Then we can actually implement bots that talk back to the opponent
		return format_prompt(my_options, opponent_options, move_damages, state_parsed, opponent_reserve_size)
		



