import constants
from data import all_move_json
from showdown.battle import Battle, State
from showdown.engine.find_state_instructions import update_attacking_move
from ..helpers import format_decision
from showdown.engine.objects import Pokemon
from pprint import pprint
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI, ChatOpenAI
from config import ShowdownConfig
from showdown.battle_bots.llm.llm_helpers import parse_choice_from_llm_output, generate_prompt_with_context
import copy

class BattleBot(Battle):
	def __init__(self, *args, **kwargs):
		super(BattleBot, self).__init__(*args, **kwargs)
		self.llm = ChatOpenAI(
				model="gpt-4o",
				temperature=0,
				max_retries=2,
				api_key=ShowdownConfig.open_ai_key,
			)

	def __deepcopy__(self, memo):
		# Create a new instance of the class without calling __init__
		new_copy = self.__class__.__new__(self.__class__)
		
		# Add new object to memo to avoid infinite recursion in case of circular references
		memo[id(self)] = new_copy

		# Manually deep copy each attribute
		for attr_name, attr_value in self.__dict__.items():
			# Check if the attribute is something that should not be deepcopied
			if attr_name in ["llm"]:  # Example of an attribute to skip deepcopying
				setattr(new_copy, attr_name, attr_value)
			else:
				# Deepcopy the attribute
				setattr(new_copy, attr_name, copy.deepcopy(attr_value, memo))

		return new_copy

	def find_best_move(self):
		prompt = generate_prompt_with_context(self)
		print("=================== PROMPT ============================\n" + prompt)
		llm_response = self.llm.invoke(prompt)
		llm_response.pretty_print()

		parse_output = None
		if llm_response:
			parse_output = parse_choice_from_llm_output(llm_response.content)
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

	def handle_win(self):
		# to do: implement a win behavior. Gloating or being humble or salty
		pass
