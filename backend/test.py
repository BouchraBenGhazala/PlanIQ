import time

print("⏱️ Démarrage du script...")
t0 = time.time()

print("1. Chargement de os/sys/dotenv...")
import os
import sys
from dotenv import load_dotenv
print(f"   ✅ Fait en {time.time()-t0:.2f}s")

t0 = time.time()
print("2. Chargement de OpenAI...")
from langchain_openai import ChatOpenAI
print(f"   ✅ Fait en {time.time()-t0:.2f}s")

t0 = time.time()
print("3. Chargement de LangGraph...")
from langgraph.prebuilt import create_react_agent
print(f"   ✅ Fait en {time.time()-t0:.2f}s")

t0 = time.time()
print("4. Chargement de Opik...")
from opik.integrations.langchain import OpikTracer 
print(f"   ✅ Fait en {time.time()-t0:.2f}s")

t0 = time.time()
print("5. Chargement de Google Tools...")
# C'est souvent ici que ça bloque
from app.agent.tools import list_calendar_events 
print(f"   ✅ Fait en {time.time()-t0:.2f}s")

print("🚀 Tout est chargé !")