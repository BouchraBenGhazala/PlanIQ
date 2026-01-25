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

# from langchain_groq import ChatGroq
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

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"Received: {request.message}")
    
    try:
        now = datetime.datetime.now()
        current_date_str = now.strftime("%A %d %B %Y")
        current_time_str = now.strftime("%H:%M")

        # Prompt 
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