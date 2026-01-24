import os
import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# AI Libraries
from langchain_google_genai import ChatGoogleGenerativeAI



from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from opik.integrations.langchain import OpikTracer

from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI

# Import all 4 tools
from app.agent.tools import (
    list_calendar_events, 
    create_calendar_event, 
    delete_calendar_event, 
    update_calendar_event
)

load_dotenv()

# 1. Initialize FastAPI
app = FastAPI(title="PlanIQ API")

# 2. Security / CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Data Model
class ChatRequest(BaseModel):
    message: str

# 4. Initialize AI Brain
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile", 
#     temperature=0
# )

llm = ChatMistralAI(
    model="mistral-small-latest", 
    temperature=0,
    api_key=os.getenv("MISTRAL_API_KEY")
)

# Register Tools
tools = [
    list_calendar_events, 
    create_calendar_event,
    delete_calendar_event,
    update_calendar_event
]

# Create the Agent Graph
agent_graph = create_react_agent(model=llm, tools=tools)

# 5. Chat Endpoint
# @app.post("/chat")
# async def chat_endpoint(request: ChatRequest):
#     print(f"Received: {request.message}")
    
#     try:
#         # Dynamic Date & Context (Marseille/France)
#         now = datetime.datetime.now()
#         current_date_str = now.strftime("%A %d %B %Y")
#         current_time_str = now.strftime("%H:%M")

#         # System Prompt with "Anti-Double-Booking" Logic
#         dynamic_system_prompt = f"""You are PlanIQ, an elite executive assistant in France (Marseille).
        
#         CONTEXT:
#         - Today is: {current_date_str}
#         - Current time: {current_time_str}
#         - Timezone: Europe/Paris (CET)
        
#         Your Capabilities:
#         1. READ: Use 'list_calendar_events' to see schedule AND internal IDs.
#         2. WRITE: Use 'create_calendar_event' to book.
#         3. MODIFY: Use 'update_calendar_event' to change time/title.
#         4. DELETE: Use 'delete_calendar_event' to cancel.

#         CRITICAL RULES:
#         - **CONFLICTS:** If 'create_calendar_event' fails because the slot is busy, tell the user clearly: "I cannot book this, you already have [Event Name] at that time." and propose a new time.
#         - **IDs:** To Modify/Delete, you MUST first run 'list_calendar_events' to find the internal ID.
#         - **PRIVACY:** NEVER show the internal ID (e.g., 'abc12345') to the user.
#         """

#         inputs = {
#             "messages": [
#                 SystemMessage(content=dynamic_system_prompt),
#                 HumanMessage(content=request.message)
#             ]
#         }
        
#         # Run Agent with Opik Tracking
#         result = agent_graph.invoke(
#             inputs,
#             config={"callbacks": [OpikTracer()]}
#         )
        
#         # Extract Response
#         final_message = result["messages"][-1]
#         raw_content = final_message.content
        
#         # Clean Output (Gemini specific)
#         clean_text = ""
#         if isinstance(raw_content, list) and len(raw_content) > 0 and isinstance(raw_content[0], dict) and "text" in raw_content[0]:
#             clean_text = raw_content[0]["text"]
#         else:
#             clean_text = str(raw_content)

#         return {"response": clean_text}

#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"Received: {request.message}")
    
    try:
        now = datetime.datetime.now()
        current_date_str = now.strftime("%A %d %B %Y")
        current_time_str = now.strftime("%H:%M")

        # Prompt renforcé pour éviter les hallucinations
        dynamic_system_prompt = f"""You are PlanIQ, an executive assistant.
        
        CONTEXT:
        - Date: {current_date_str}
        - Time: {current_time_str}
        
        RULES FOR TOOLS:
        1. REALITY CHECK: Do NOT say you created an event unless the 'create_calendar_event' tool returned "Success".
        2. VERIFICATION: If you are unsure, check the calendar with 'list_calendar_events' first.
        3. SILENCE: Don't imagine fake confirmations. Only report what the tools output.
        """

        inputs = {
            "messages": [
                SystemMessage(content=dynamic_system_prompt),
                HumanMessage(content=request.message)
            ]
        }
        
        result = agent_graph.invoke(
            inputs,
            config={"callbacks": [OpikTracer()]}
        )
        
        final_message = result["messages"][-1]
        return {"response": final_message.content}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


    
@app.get("/")
async def health_check():
    return {"status": "PlanIQ Brain is online!"}