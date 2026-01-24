from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from app.agent.tools import list_calendar_events 
from opik.integrations.langchain import OpikTracer 

load_dotenv()

def run_agent():
    print("🤖 Initializing PlanIQ Agent (With Custom Persona)...")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    tools = [list_calendar_events]

    # --- 💡 THE BRAIN: SYSTEM PROMPT ---
    # This is where you tell the AI how to behave.
    # We make it an "Executive Assistant" instead of a generic bot.
    system_message = """You are PlanIQ, an elite executive productivity assistant.
    Your goal is to help the user manage their time efficiently.
    
    Your capabilities:
    1. You have direct access to the user's Google Calendar via tools.
    2. When asked about the schedule, ALWAYS use the 'list_calendar_events' tool first.
    3. Don't just list events; analyze them. If the user is busy, say "You have a packed day."
    4. Keep your answers concise and professional.
    """

    # We build the prompt structure
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}"),
        # ⚠️ CRITICAL: This placeholder is where the AI "thinks" and calls tools
        ("placeholder", "{agent_scratchpad}"), 
    ])

    # Construct the Agent
    agent = create_agent(llm, tools, prompt)
    # agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Test Query
    query = "Do I have any free time today?"
    
    print(f"\n👤 User: {query}")
    print("🤖 Agent is thinking...\n")

    try:
        response = agent.invoke(
            {"input": query},
            config={"callbacks": [OpikTracer()]} 
        )
        print("\n🏁 Final AI Response:")
        print(response['output'])

    except Exception as e:
        print(f"❌ Error running agent: {e}")

if __name__ == "__main__":
    run_agent()