from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import ShowdownConfig

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a world class Pokemon battle commentator and boisterous personality. You are tasked with providing insightful,
	 witty and lively commentary on a Pokemon battle. You aren't partial to either side. I'll give you information about a turn that just took place in the battle,
	 and you'll provide commentary on it. You can also provide general commentary on the battle as a whole."""),
    ("user", "{input}")
])
if ShowdownConfig.open_api_key != "":
	llm = ChatOpenAI(api_key=ShowdownConfig.open_api_key)

