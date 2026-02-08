import os
import datetime
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# AI Libraries
from langchain_mistralai import ChatMistralAI # Using Mistral as you requested
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from opik.integrations.langchain import OpikTracer

# Import tools
from app.agent.tools import (
    list_calendar_events, 
    create_calendar_event, 
    delete_calendar_event, 
    update_calendar_event
)

api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    print(" ERROR: MISTRAL_API_KEY is missing in .env file!")


load_dotenv()

app = FastAPI(title="PlanIQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

# Initialize AI (Mistral)
llm = ChatMistralAI(
    model="mistral-small-latest", 
    temperature=0,
    api_key=os.getenv("MISTRAL_API_KEY")
)

tools = [
    list_calendar_events, 
    create_calendar_event, 
    delete_calendar_event, 
    update_calendar_event
]

agent_graph = create_react_agent(model=llm, tools=tools)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"Received context with {len(request.messages)} messages")
    
    try:
        # 1. Precise Date Context
        now = datetime.datetime.now()
        current_date_str = now.strftime("%A, %d %B %Y") # e.g. "Monday, 26 January 2026"
        current_time_str = now.strftime("%H:%M")       # e.g. "14:30"

        # 2. THE "STRICT" SYSTEM PROMPT
        # This prevents hallucinations by forcing a specific process.
        dynamic_system_prompt = f"""You are PlanIQ, a strict and precise executive assistant.

        CURRENT CONTEXT:
        - Today is: {current_date_str}
        - Current time: {current_time_str}
        - Timezone: Europe/Paris
        
        YOUR TOOLS:
        1. list_calendar_events: REQUIRED to find event IDs.
        2. create_calendar_event: Books new slots (checks conflicts automatically).
        3. delete_calendar_event: Requires an 'event_id'.
        4. update_calendar_event: Requires an 'event_id'.

        VERY CRITICAL RULES (DO NOT IGNORE):
        
        1. **NO GUESSING IDs:** If the user asks to "Delete/Update", you MUST run 'list_calendar_events' FIRST to find the internal 'event_id'. Do NOT guess the ID.
        
        2. **VERIFY SUCCESS:** 
           - Call the tool.
           - OBLIGATORY : If the tool is update_calendar_event or delete_calendar_event, call list_calendar_events first to get the event_id!!
           - READ the tool's output.
           - If the tool says "SUCCESS", tell the user "Done".
           - If the tool says "ERROR" or "FAILURE", tell the user exactly what went wrong.
           - NEVER say "I updated it" or "I deleted it" if the tool returned an error.

        3. **BE SPECIFIC:** 
            - Don't answer questions out of the scope of calendar management and scheduling.
            - Do not provide the event link or event id unless the user specifically ask to keep the chat clean.

        4. **BE HONEST:** If you are unsure, say "Let me check your calendar first" and run the list tool.
        """

        # 3. Rebuild History
        langchain_messages = [SystemMessage(content=dynamic_system_prompt)]
        for msg in request.messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))

        # 4. Run Agent
        inputs = {"messages": langchain_messages}
        
        result = agent_graph.invoke(
            inputs,
            config={"callbacks": [OpikTracer()]}
        )

        #ADDED TO CHECK
        # --- DEBUG LOGGING ---
        print("--- AGENT OUTPUT DEBUG ---")
        final_message = result["messages"][-1]
        print(f"Final Message Content: '{final_message.content}'")
        print("--------------------------")

        # If content is empty (common error with Mistral tools), fallback
        response_text = final_message.content
        if not response_text:
            print("I'm sorry, I encountered an error processing that request. (Empty Response)")

            

        # LOGGING SYSTEM: See what the agent did in your Terminal
        print("--- AGENT REASONING LOG ---")
        for m in result['messages']:
            if isinstance(m, AIMessage) and m.tool_calls:
                for tool_call in m.tool_calls:
                    print(f" AI DECIDED TO CALL: {tool_call['name']} with args: {tool_call['args']}")
            elif isinstance(m, ToolMessage):
                print(f"TOOL RESULT: {m.content}")
        print("--------------------------------")
        
        final_message = result["messages"][-1]
        return {"response": final_message.content}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def health_check():
    return {"status": "PlanIQ Brain is online!"}