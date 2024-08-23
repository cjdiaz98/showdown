from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import ShowdownConfig
import json 
import logging
from showdown.Commentary.parsingUtils import parseMessagesIntoEventDicts

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class LLMCommentator():
	promptTemplate = ChatPromptTemplate.from_messages([
	("system", """You are a world class Pokemon battle commentator and boisterous personality living in the fictional world of Pokemon. You are tasked with providing
	 witty and lively commentary on a real-time Pokemon battle (which the listeners are also watching). You aren't partial to either side.
  	I'll give you information about a turn that just took place in the battle,
	as well as some previous commentary describing what previously happened in the battle. In return you'll provide commentary 
  	and battle analysis that paints a picture of what just happened.\
  	You can also provide general commentary on the battle as a whole. Please keep your commentary concise and do not tell the listeners to stay tuned."""),
	 ("ai", "{previous_turn}"),
	("human", "{turn_data}")
	])
	previous_round = "The battle has just begun!"

	def __init__(self):
		ShowdownConfig.configure()
		if ShowdownConfig.open_ai_key != None:
			self.llm = ChatOpenAI(
				model="gpt-4o",
				temperature=0,
				max_tokens=None,
				timeout=None,
				max_retries=2,
				api_key=ShowdownConfig.open_ai_key,
				# base_url="...",
				# organization="...",
				# other params...
			)
		self.logger = logging.getLogger(__name__)

	def get_commentary(self, turn_data: str):
		if self.llm is None:
			return "No OpenAI key provided. Cannot generate commentary."
		
		self.logger.debug(turn_data)
		try:
			# Try parsing the turn data
			parsed_turn_data = parseMessagesIntoEventDicts(turn_data)
		except Exception as e:
			# Log the exception and use a fallback mechanism
			self.logger.error(f"Error parsing turn data: {e}")
			parsed_turn_data = {"error": "Could not parse turn data"}
		turn_data = "Current turn: \n" + json.dumps(parsed_turn_data, separators=(',', ':'))
		prompt = self.promptTemplate.format_messages(previous_turn = self.previous_round, turn_data = turn_data)
		# print(prompt)
		commentary = self.llm.invoke(prompt)
		self.previous_round = commentary.content
		return commentary

def getCommentaryOnTurns(turns: dict[int, dict]) -> list[str]:
	# Really only to be used when reading logs from a battle
	llm_commentator = LLMCommentator()
	turn_commentary = []
	for turn_number, turn_data in turns.items():
		json_object = json.dumps(turn_data, separators=(',', ':')) # make the json more compact
		commentary = llm_commentator.get_commentary(json_object)
		commentary = 'Turn {turn_no}\n'.format(turn_no = turn_number) + commentary.content + "\n"
		turn_commentary.append(commentary)
	return turn_commentary
