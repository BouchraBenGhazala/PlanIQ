import os
import datetime
from dotenv import load_dotenv
from langchain.tools import tool
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

def get_calendar_service():
    """Helper function to authenticate with Google (Do not modify)."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

# --- THE TOOL THE AI WILL USE ---

@tool
def list_calendar_events():
    """
    Use this tool to check the user's schedule.
    It returns a list of the upcoming events from the calendar.
    """
    try:
        service = get_calendar_service()
        # Get current time in UTC
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        
        if not events:
            return "No upcoming events found."
            
        # Format the result clearly for the AI
        results = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event["summary"]
            results.append(f"- {start}: {summary}")
            
        return "\n".join(results)

    except Exception as e:
        return f"Error fetching calendar: {str(e)}"

# --- TOOL 2: CREATE EVENT ---
@tool
def create_calendar_event(summary: str, start_time: str, duration_minutes: int = 60):
    """
    Use this tool to BOOK a new meeting or task.
    
    Args:
        summary: The title of the event (e.g., "Interview", "Meeting with Antoine").
        start_time: The start time in ISO format (e.g., "2026-01-25T14:00:00").
        duration_minutes: How long the event lasts (default is 60 minutes).
    """
    try:
        service = get_calendar_service()
        
        # Calculate End Time
        start_dt = datetime.datetime.fromisoformat(start_time)
        end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
        
        event_body = {
            'summary': summary,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Europe/Paris',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Europe/Paris',
            },
        }

        event = service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()
        
        return f"Success! Event '{summary}' created. Link: {event.get('htmlLink')}"

    except Exception as e:
        return f"Failed to create event: {str(e)}"