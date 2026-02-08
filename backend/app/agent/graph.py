import os
from dotenv import load_dotenv

# LLM
from langchain_mistralai import ChatMistralAI
# (Or ChatGoogleGenerativeAI if you switch back)

# LangGraph
from langgraph.prebuilt import create_react_agent

# Tools
from app.agent.tools import (
    list_calendar_events, 
    create_calendar_event, 
    delete_calendar_event, 
    update_calendar_event
)

load_dotenv()

# 1. Initialize the Model
# We do this here so main.py doesn't get cluttered
llm = ChatMistralAI(
    model="mistral-small-latest", 
    temperature=0,
    api_key=os.getenv("MISTRAL_API_KEY")
)

# 2. Define the Tools List
tools = [
    list_calendar_events, 
    create_calendar_event, 
    delete_calendar_event, 
    update_calendar_event
]

# 3. Create the Agent Graph
# This variable 'agent_graph' is what we will import in main.py
agent_graph = create_react_agent(model=llm, tools=tools)