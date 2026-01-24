import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
# On importe SystemMessage en plus de HumanMessage
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from opik.integrations.langchain import OpikTracer 

from app.agent.tools import list_calendar_events 

load_dotenv()

def run_agent():
    print("🤖 Initializing PlanIQ Agent (Robust Version)...")

    # 1. Initialize Model
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    # 2. Tools
    tools = [list_calendar_events]

    # 3. System Prompt (Your Persona)
    system_message_content = """You are PlanIQ, an elite executive productivity assistant.
    Your goal is to help the user manage their time efficiently.
    
    Your capabilities:
    1. You have direct access to the user's Google Calendar via tools.
    2. When asked about the schedule, ALWAYS use the 'list_calendar_events' tool first.
    3. Don't just list events; analyze them. If the user is busy, say "You have a packed day."
    4. Keep your answers concise and professional.
    """

    # 4. Create the Agent (WITHOUT arguments that cause errors)
    # We remove 'state_modifier'. We will pass the prompt manually below.
    agent_graph = create_react_agent(
        model=llm, 
        tools=tools
    )

    query = "What do I have planned coming up in my schedule?"
    
    print(f"\n👤 User: {query}")
    print("🤖 Agent is thinking...\n")

    try:
        # 5. Execute with Manual System Message
        # We manually put the SystemMessage FIRST in the list.
        # This works on ALL versions of LangGraph.
        inputs = {
            "messages": [
                SystemMessage(content=system_message_content), #  The Persona is here
                HumanMessage(content=query)                    #  The User Question
            ]
        }
        
        response = agent_graph.invoke(
            inputs,
            config={"callbacks": [OpikTracer()]} 
        )

        final_message = response["messages"][-1]
        raw_content = final_message.content

        print("\n🏁 Final AI Response (Cleaned):")
        print(raw_content[0]["text"])

    except Exception as e:
        print(f"❌ Error running agent: {e}")

if __name__ == "__main__":
    run_agent()