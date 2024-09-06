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
from showdown.battle_bots.llm.llm_helpers import parse_choice_from_llm_output, generate_prompt_with_context, parse_commentary_from_llm_output
import copy
from showdown.websocket_client import PSWebsocketClient
import asyncio
from concurrent.futures import ThreadPoolExecutor
from showdown.Commentary.parsingUtils import chunk_message_smartly

class BattleBot(Battle):
	def __init__(self, *args, ps_websocket_client:PSWebsocketClient =None, **kwargs):
		"""
		Initializes the BattleBot for the 'llm' module, allowing the ps_websocket_client to be passed optionally.
		
		Args:
			*args: Regular positional arguments for the superclass.
			ps_websocket_client (PsWebsocketClient, optional): Websocket client for managing interactions with the server.
			**kwargs: Keyword arguments for the superclass.
		"""
		super(BattleBot, self).__init__(*args, **kwargs)
		
		# Assign the websocket client if it's provided
		self.websocket_client = ps_websocket_client
		
		self.llm = ChatOpenAI(
				model="gpt-4o",
				temperature=0,
				max_retries=2,
				api_key=ShowdownConfig.open_ai_key,
			)
		self.executor = ThreadPoolExecutor()

	def __deepcopy__(self, memo):
		# Create a new instance of the class without calling __init__
		new_copy = self.__class__.__new__(self.__class__)
		
		# Add new object to memo to avoid infinite recursion in case of circular references
		memo[id(self)] = new_copy

		# Manually deep copy each attribute
		for attr_name, attr_value in self.__dict__.items():
			# Check if the attribute is something that should not be deepcopied
			if attr_name in ["llm", "websocket_client", "executor"]:  # attributes to skip deepcopying
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

		parse_choice_output = None
		if llm_response:
			parse_choice_output = parse_choice_from_llm_output(llm_response.content)
			parse_commentary_output = parse_commentary_from_llm_output(llm_response.content)

		# to do: See if we want to list a stop sequence such as "END"
		if not parse_choice_output:
			return None
		if self.websocket_client and parse_commentary_output:
			commentary_chunked = chunk_message_smartly(300, parse_commentary_output)
			self._send_message_in_chat_async(commentary_chunked)

		# if self.force_switch or not moves: # How do we handle a forced switch?
		decision = format_decision(self, parse_choice_output[0])

		if len(parse_choice_output) > 1 and not constants.TERASTALLIZE in parse_choice_output[0] and parse_choice_output[1].lower().startsWith(constants.TERASTALLIZE):
			# format decision to have tera if the LLM decided it and not already present
			decision[0] = decision[0] + " " + constants.TERASTALLIZE

		return decision

	async def _send_message_in_chat(self, message_list: list[str]):
		await self.websocket_client.send_message(self.battle_tag, message_list)
	
	def _send_message_in_chat_async(self, message_list: list[str]):
		"""Wraps the async message sending in an executor to run in sync context."""
		# Using `asyncio.run()` directly within the executor to ensure a new event loop is created.
		loop = asyncio.new_event_loop()
		asyncio.run_coroutine_threadsafe(self._send_message_in_chat(message_list), loop)
		loop.run_until_complete(loop.shutdown_asyncgens())  # To ensure all generators complete
		loop.close()
		
	def get_all_switch_options(self):
		return [action for action in self.get_all_options() if action.startswith(constants.SWITCH_STRING + " ")]

	def handle_win(self):
		# to do: implement a win behavior. Gloating or being humble or salty
		pass
