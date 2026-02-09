
# PlanIQ: The Agentic Productivity Architect

**Submission for Milestone: Mid-Hackathon Checkpoint**

PlanIQ is not just a chatbot; it is an **autonomous AI Agent** designed to actively manage your time. Unlike passive to-do lists, PlanIQ integrates directly with **Google Calendar** to read your schedule, reason about your availability, and perform actions (booking, rescheduling, or cancelling) on your behalf.

Built with **LangGraph**, **FastAPI**, and observed via **Comet Opik**.

---

## Current Progress & Features
We have successfully built the "Brain" (Backend) of the application.

*   **Agentic Core:** Implemented a reasoning loop using `LangGraph` (ReAct pattern).
*   **Full Calendar Control:** The Agent has 4 custom tools:
    *   `list_calendar_events`: Reads schedule & retrieves internal IDs.
    *   `create_calendar_event`: Books slots with anti-double-booking logic.
    *   `update_calendar_event`: Reschedules or renames events.
    *   `delete_calendar_event`: Cancels meetings.
*   **Context Awareness:** The Agent knows the current date, time, and timezone (Europe/Paris), preventing hallucinated dates.
*   **Observability:** Full integration with **Opik** to track the Agent's reasoning traces, tool calls, and latency.
*   **API Layer:** A FastAPI server exposing the agent via REST endpoints.

---

## Tech Stack
*   **Runtime:** Python 3.10+
*   **Framework:** FastAPI
*   **AI Orchestration:** LangChain & LangGraph
*   **LLM:** Mistral AI (or Google Gemini/OpenAI - model agnostic)
*   **Observability:** Comet Opik
*   **External API:** Google Calendar API

---

## Installation & Setup Guide

Since this project deals with sensitive API keys and OAuth credentials, they are not included in the repository. Follow these steps to reproduce the environment.

### 1. Clone & Environment
```bash
git clone https://github.com/YOUR_USERNAME/PlanIQ.git
cd PlanIQ/backend

# Create and activate virtual environment
python3 -m venv planiq_venv
source planiq_venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Calendar API Setup (Crucial)
To allow the AI to control the calendar, you must set up a Google Cloud Project:

1.  Go to **Google Cloud Console**.
2.  Create a new project and enable the **Google Calendar API**.
3.  **OAuth Consent Screen:** Set to "External" and add your email as a "Test User".
4.  **Credentials:** Create an "OAuth 2.0 Client ID" (Desktop Application).
5.  **Download JSON:** Download the client secret file, rename it to `credentials.json`, and place it inside the `backend/` folder.
    *   *Note: This file is ignored by git for security.*
6.  **Test Calendar:** Create a secondary calendar in Google Calendar settings to use for testing (safer than your primary one). Copy its **Calendar ID** (e.g., `abc12345@group.calendar.google.com`).

### 3. Environment Variables (.env)
Create a `.env` file in the `backend/` folder and add the following keys:

```ini
# --- LLM API KEYS (Choose your provider) ---
MISTRAL_API_KEY=your_mistral_key_here
# or GOOGLE_API_KEY=your_gemini_key_here

# --- OBSERVABILITY (The Tech Prize) ---
OPIK_API_KEY=your_comet_opik_key_here
OPIK_PROJECT_NAME=PlanIQ

# --- CALENDAR CONFIG ---
GOOGLE_CALENDAR_ID=your_test_calendar_id@group.calendar.google.com
```

### 4. First Run Authentication
The first time you run the application, it will open a browser window to authenticate with Google.
1.  Run the server (see below).
2.  Log in with the Google Account added as a "Test User".
3.  Authorize the app.
4.  A `token.json` file will be generated automatically in `backend/`. This stores the session token.

---

## Running the Backend "Brain"

We use **Uvicorn** to run the FastAPI server.

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, you should see:
> `INFO: PlanIQ Brain is online!`

### Testing via Swagger UI
You can test the Agent without a frontend using the automatic docs:

1.  Open **http://localhost:8000/docs**
2.  Go to `POST /chat` -> **Try it out**.
3.  Send a JSON request:
    ```json
    {
      "message": "Book a meeting called 'Deep Work' for tomorrow at 10 AM."
    }
    ```
4.  **Verification:** Check your Google Calendar to see the event appear!

---

## Observability with Opik
Every interaction is traced to verify the Agent's reliability.
1.  Log in to [Comet.com](https://wwHere is a professional, comprehensive, and "Judge-Ready" **README.md** file.

You can copy and paste this directly into your GitHub repository. It clearly explains the technical complexity, the steps you have completed, and how to replicate the setup (which is crucial since you are hiding secrets).

***

# PlanIQ: The Agentic Productivity Architect

**Submission for Milestone: Mid-Hackathon Checkpoint**

PlanIQ is not just a chatbot; it is an **autonomous AI Agent** designed to actively manage your time. Unlike passive to-do lists, PlanIQ integrates directly with **Google Calendar** to read your schedule, reason about your availability, and perform actions (booking, rescheduling, or cancelling) on your behalf.

Built with **LangGraph**, **FastAPI**, and observed via **Comet Opik**.

---

## Current Progress & Features
We have successfully built the "Brain" (Backend) of the application.

*   **Agentic Core:** Implemented a reasoning loop using `LangGraph` (ReAct pattern).
*   **Full Calendar Control:** The Agent has 4 custom tools:
    *   `list_calendar_events`: Reads schedule & retrieves internal IDs.
    *   `create_calendar_event`: Books slots with anti-double-booking logic.
    *   `update_calendar_event`: Reschedules or renames events.
    *   `delete_calendar_event`: Cancels meetings.
*   **Context Awareness:** The Agent knows the current date, time, and timezone (Europe/Paris), preventing hallucinated dates.
*   **Observability:** Full integration with **Opik** to track the Agent's reasoning traces, tool calls, and latency.
*   **API Layer:** A FastAPI server exposing the agent via REST endpoints.

---

## Tech Stack
*   **Runtime:** Python 3.10+
*   **Framework:** FastAPI
*   **AI Orchestration:** LangChain & LangGraph
*   **LLM:** Mistral AI (or Google Gemini/OpenAI - model agnostic)
*   **Observability:** Comet Opik
*   **External API:** Google Calendar API

---

##  Installation & Setup Guide

Since this project deals with sensitive API keys and OAuth credentials, they are not included in the repository. Follow these steps to reproduce the environment.

### 1. Clone & Environment
```bash
git clone https://github.com/YOUR_USERNAME/PlanIQ.git
cd PlanIQ/backend

# Create and activate virtual environment
python3 -m venv planiq_venv
source planiq_venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Calendar API Setup (Crucial)
To allow the AI to control the calendar, you must set up a Google Cloud Project:

1.  Go to **Google Cloud Console**.
2.  Create a new project and enable the **Google Calendar API**.
3.  **OAuth Consent Screen:** Set to "External" and add your email as a "Test User".
4.  **Credentials:** Create an "OAuth 2.0 Client ID" (Desktop Application).
5.  **Download JSON:** Download the client secret file, rename it to `credentials.json`, and place it inside the `backend/` folder.
    *   *Note: This file is ignored by git for security.*
6.  **Test Calendar:** Create a secondary calendar in Google Calendar settings to use for testing (safer than your primary one). Copy its **Calendar ID** (e.g., `abc12345@group.calendar.google.com`).

### 3. Environment Variables (.env)
Create a `.env` file in the `backend/` folder and add the following keys:

```ini
# --- LLM API KEYS (Choose your provider) ---
MISTRAL_API_KEY=your_mistral_key_here
# or GOOGLE_API_KEY=your_gemini_key_here

# --- OBSERVABILITY (The Tech Prize) ---
OPIK_API_KEY=your_comet_opik_key_here
OPIK_PROJECT_NAME=PlanIQ

# --- CALENDAR CONFIG ---
GOOGLE_CALENDAR_ID=your_test_calendar_id@group.calendar.google.com
```

### 4. First Run Authentication
The first time you run the application, it will open a browser window to authenticate with Google.
1.  Run the server (see below).
2.  Log in with the Google Account added as a "Test User".
3.  Authorize the app.
4.  A `token.json` file will be generated automatically in `backend/`. This stores the session token.

---

## Running the Backend "Brain"

We use **Uvicorn** to run the FastAPI server.

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, you should see:
> `INFO: PlanIQ Brain is online!`

### Testing via Swagger UI
You can test the Agent without a frontend using the automatic docs:

1.  Open **http://localhost:8000/docs**
2.  Go to `POST /chat` -> **Try it out**.
3.  Send a JSON request:
    ```json
    {
      "message": "Book a meeting called 'Deep Work' for tomorrow at 10 AM."
    }
    ```
4.  **Verification:** Check your Google Calendar to see the event appear!

---

## Observability with Opik
Every interaction is traced to verify the Agent's reliability.
1.  Log in to [Comet.com](https://www.comet.com).
2.  Navigate to the **PlanIQ** project in the Opik dashboard.
3.  You can view the full "Chain of Thought":
    *   User Input -> LLM Reasoning -> Tool Execution (e.g., `create_calendar_event`) -> Final Response.

---

Here is the section you can add at the very end of your `README.md`:

---

## Demo & Screenshots

I have included a **Demo File** (see the `screenshots/` folder) to showcase the project in action.

**This demo includes proof of:**
1.  **Real-time Calendar Interaction:** Screenshots of events being booked and deleted by the Agent in Google Calendar.
2.  **Opik Observability:** Traces from the Comet dashboard proving the Agent's reasoning loop and tool usage.
3.  **API Testing:** Successful request/response cycles via the FastAPI Swagger UI.

---
Here is the text to add to the bottom of your `README.md`. I have written it to highlight the technical complexity of your deployment (handling OAuth on a server) and the rigor of your evaluation pipeline.

You can copy and paste this section directly to the end of your file.

***

## Deployment Architecture

The application is deployed as a distributed system to ensure scalability and separation of concerns.

**Live Demo:** [https://planiq-demo.vercel.app/](https://planiq-demo.vercel.app/)

### 1. Backend (Render)
*   **Platform:** Hosted on **Render** (Python/FastAPI).
*   **Headless Authentication:**
    *   Since Render cannot open a browser for Google OAuth, we implemented a robust solution using a `GOOGLE_TOKEN_JSON` environment variable.
    *   The local `token.json` is serialized and injected into the cloud environment, allowing the agent to authenticate securely without manual intervention.
*   **Keep-Alive:** A Cron-job pings the backend every 5 minutes to prevent "Cold Starts," ensuring the Agent is always ready to respond instantly.

### 2. Frontend (Vercel)
*   **Platform:** Hosted on **Vercel** (Next.js/React).
*   **Connectivity:** connect to the backend via the `NEXT_PUBLIC_API_URL` environment variable (`https://planiq-backend.onrender.com`).
*   **Chat Interface:** Provides a clean, chat-based UI that handles the JSON communication with the FastAPI agent.

---

## AI Evaluation & Testing (Comet Opik)

To ensure **PlanIQ** is reliable enough for executive use, we moved beyond simple "vibes-based" testing. We implemented a rigorous **LLM-as-a-Judge** evaluation pipeline using **Comet Opik**.

### 1. The Dataset
We created a curated dataset covering critical edge cases to prevent common AI failures:
*   **Conflict Handling:** Trying to book a slot that is already taken.
*   **Safety Protocols:** Attempting to delete an event without finding its ID first.
*   **Date Logic:** Relative dates (e.g., "Next Friday at 3 PM").

### 2. The Evaluation Rules
We defined three specific metrics to score the Agent's performance automatically:

| Metric | Type | Purpose |
| :--- | :--- | :--- |
| **Answer Relevance** | `LLM-as-a-Judge` | **Sanity Check:** Did the model address the user's prompt or hallucinate something unrelated? |
| **Result Accuracy** | `Meaning Match` | **Outcome Verification:** Compares the Agent's final text response against the "Ground Truth" (e.g., Expected "Failure due to conflict", Agent said "Success" -> **Fail**). |
| **Tool Compliance** | `Custom Judge` | **Logic Verification:** A strict technical check. It reads the execution trace to ensure the *correct code functions* were called in the *correct order* (e.g., `list_events` must happen before `delete_event`). |

### 3. Continuous Improvement
By running this evaluation suite, we can confidently deploy updates, knowing that the Agent respects the user's calendar integrity and follows all safety protocols.