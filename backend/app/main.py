import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import AI components
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
# 👇 On utilise la structure robuste (System + Human)
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from opik.integrations.langchain import OpikTracer

# 👇 IMPORT DES DEUX OUTILS (Lecture + Écriture)
# Assure-toi que create_calendar_event est bien dans tools.py !
from app.agent.tools import list_calendar_events, create_calendar_event

load_dotenv()

# 1. Initialize FastAPI App
app = FastAPI(title="PlanIQ API")

# 2. Configure CORS (Open to everyone for testing)
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

# 4. Initialize Agent (The Brain)
# On utilise le même modèle qui a marché pour toi
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# On donne les super-pouvoirs (Lecture ET Écriture)
tools = [list_calendar_events, create_calendar_event]

# Le Prompt Système "Expert"
system_message_content = """You are PlanIQ, an elite executive productivity assistant.
Your goal is to help the user manage their time efficiently.

Your Capabilities:
1. READ: You can check the user's schedule using 'list_calendar_events'.
2. WRITE: You can BOOK new tasks or meetings using 'create_calendar_event'.

Rules:
- If the user asks to "book", "schedule", or "block time", use 'create_calendar_event'.
- ALWAYS check the schedule ('list_calendar_events') BEFORE booking to avoid double-booking.
- If the user doesn't specify a time, ask them for it.
- Keep your answers concise and professional.
"""

# Création de l'agent (Sans arguments compliqués, comme dans ton test qui marche)
agent_graph = create_react_agent(model=llm, tools=tools)

# 5. The API Endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"📩 Received: {request.message}")
    
    try:
        # On construit les messages manuellement (La méthode robuste)
        inputs = {
            "messages": [
                SystemMessage(content=system_message_content),
                HumanMessage(content=request.message)
            ]
        }
        
        # Exécution avec Tracking Opik
        result = agent_graph.invoke(
            inputs,
            config={"callbacks": [OpikTracer()]}
        )
        
        # Extraction de la réponse
        final_message = result["messages"][-1]
        raw_content = final_message.content
        
        # Nettoyage du format Gemini (La partie importante !)
        clean_text = ""
        
        # Gemini renvoie parfois une liste de dictionnaires, parfois du texte
        if isinstance(raw_content, list) and len(raw_content) > 0 and isinstance(raw_content[0], dict) and "text" in raw_content[0]:
            clean_text = raw_content[0]["text"]
        else:
            # Si c'est déjà du texte ou un autre format simple
            clean_text = str(raw_content)

        return {"response": clean_text}

    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def health_check():
    return {"status": "PlanIQ Brain is online 🧠"}