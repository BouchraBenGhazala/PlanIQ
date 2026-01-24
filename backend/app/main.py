import os
import datetime # Important for date calculation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# AI Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from opik.integrations.langchain import OpikTracer

# Import Tools
from app.agent.tools import list_calendar_events, create_calendar_event

load_dotenv()

# 1. Initialize FastAPI App
app = FastAPI(title="PlanIQ API")

# 2. Configure CORS (Open to everyone for testing purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Data Model for incoming requests
class ChatRequest(BaseModel):
    message: str

# 4. Initialize Agent (The Brain)
# We use Gemini 2.5 Flash as it is fast and free
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# We define the tools available to the Agent (Read + Write)
tools = [list_calendar_events, create_calendar_event]

# Create the Agent (we don't pass the system prompt here, we do it dynamically per request)
agent_graph = create_react_agent(model=llm, tools=tools)

# 5. The API Endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"Received: {request.message}")
    
    try:
        # DYNAMIC CONTEXT: Get current date and time (France)
        now = datetime.datetime.now()
        current_date_str = now.strftime("%A %d %B %Y") 
        current_time_str = now.strftime("%H:%M")  

        # DYNAMIC PROMPT: We inject the date so the AI understands "Tomorrow"
        dynamic_system_prompt = f"""You are PlanIQ, an elite executive productivity assistant in France (Marseille).
        
        CONTEXT:
        - Today is: {current_date_str}
        - Current time: {current_time_str}
        - Timezone: Europe/Paris (CET)
        
        Your Capabilities:
        1. READ: Check schedule using 'list_calendar_events'.
        2. WRITE: BOOK meetings using 'create_calendar_event'.

        Rules:
        - If user says "tomorrow", calculate the date based on "Today is {current_date_str}".
        - ALWAYS check the schedule ('list_calendar_events') BEFORE booking to avoid double-booking.
        - If the user doesn't specify a time, ask them for it.
        - Keep your answers concise and professional.
        """

        # Prepare messages
        inputs = {
            "messages": [
                SystemMessage(content=dynamic_system_prompt),
                HumanMessage(content=request.message)
            ]
        }
        
        # Execute the Agent (with Opik Tracking for the prize)
        result = agent_graph.invoke(
            inputs,
            config={"callbacks": [OpikTracer()]}
        )
        
        # Extract the final response
        final_message = result["messages"][-1]
        raw_content = final_message.content
        
        # Clean Gemini Response (Handle specific JSON format if necessary)
        clean_text = ""
        if isinstance(raw_content, list) and len(raw_content) > 0 and isinstance(raw_content[0], dict) and "text" in raw_content[0]:
            clean_text = raw_content[0]["text"]
        else:
            clean_text = str(raw_content)

        return {"response": clean_text}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def health_check():
    return {"status": "PlanIQ Brain is online "}