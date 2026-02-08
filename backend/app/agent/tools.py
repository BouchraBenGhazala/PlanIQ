import os
import datetime
import zoneinfo # Standard in Python 3.9+
from dotenv import load_dotenv
from langchain.tools import tool
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Define scopes (Read/Write access)
SCOPES = ["https://www.googleapis.com/auth/calendar"]
# Get Calendar ID (Defaults to primary if not set in .env)
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")
# Define the specific timezone for France
PARIS_TZ = zoneinfo.ZoneInfo("Europe/Paris")

def get_calendar_service():
    """
    Authenticates with Google and returns the API service.
    Handles token refresh automatically.
    """
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

# --- TOOL 1: READ EVENTS ---
@tool
def list_calendar_events():
    """
    Use this tool to check the user's schedule.
    It returns a list of upcoming events WITH THEIR IDs.
    
    IMPORTANT: You MUST use this tool to find the 'event_id' before 
    updating or deleting an event.
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
            
        results = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event["summary"]
            event_id = event["id"] # Capture the ID
            
            # Format: [ID: xxxxx] - Date: Title
            results.append(f"[ID: {event_id}] - {start}: {summary}")
            
        return "\n".join(results)

    except Exception as e:
        return f"Error fetching calendar: {str(e)}"

# --- TOOL 2: CREATE EVENT (With Conflict Check) ---
@tool
def create_calendar_event(summary: str, start_time: str, duration_minutes: int = 60):
    """
    Use this tool to BOOK a new meeting or task.
    It AUTOMATICALLY checks if the slot is free before booking.
    
    Args:
        summary: The title of the event (e.g., "Deep Work").
        start_time: The start time in ISO format (e.g., "2026-01-25T14:00:00").
        duration_minutes: How long the event lasts (default is 60 minutes).
    """
    try:
        service = get_calendar_service()
        
        # 1. Parse dates and apply Paris Timezone
        # We replace 'Z' just in case the AI adds it, to treat string as compatible
        dt_naive = datetime.datetime.fromisoformat(start_time.replace("Z", ""))
        start_dt_paris = dt_naive.replace(tzinfo=PARIS_TZ)
        end_dt_paris = start_dt_paris + datetime.timedelta(minutes=duration_minutes)
        
        # 2. CONFLICT CHECK: Convert to UTC for search
        # Google API prefers UTC for filtering
        start_dt_utc = start_dt_paris.astimezone(datetime.timezone.utc)
        end_dt_utc = end_dt_paris.astimezone(datetime.timezone.utc)

        print(f"🔎 Checking conflicts between {start_dt_utc} and {end_dt_utc}...")
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_dt_utc.isoformat(),
            timeMax=end_dt_utc.isoformat(),
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        conflicts = events_result.get("items", [])
        
        # 3. If conflicts exist, STOP and return error
        if conflicts:
            conflict_summary = conflicts[0]['summary']
            print(f"Conflict detected: {conflict_summary}")
            # The capitalized "FAILURE" helps the AI understand it went wrong
            return f"FAILURE: Cannot book '{summary}'. The time slot is ALREADY TAKEN by '{conflict_summary}'. Stop and tell the user about this conflict."

        # 4. If slot is free, proceed with booking
        print("Slot free. Booking now...")
        event_body = {
            'summary': summary,
            'start': {
                'dateTime': start_dt_paris.isoformat(),
                'timeZone': 'Europe/Paris', # Force Paris Timezone
            },
            'end': {
                'dateTime': end_dt_paris.isoformat(),
                'timeZone': 'Europe/Paris',
            },
        }

        event = service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()
        return f"SUCCESS! Event '{summary}' created. Link: {event.get('htmlLink')}"

    except Exception as e:
        print(f"System Error: {e}")
        return f"Error creating event: {str(e)}"

# --- TOOL 3: DELETE EVENT ---
@tool
def delete_calendar_event(event_id: str):
    """
    Use this tool to CANCEL or DELETE an event.
    You must provide the 'event_id' found using 'list_calendar_events'.
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        return "SUCCESS! Event deleted."
    except Exception as e:
        return f"Failed to delete event: {str(e)}"

# --- TOOL 4: UPDATE EVENT ---
@tool
def update_calendar_event(event_id: str, new_start_time: str = None, new_summary: str = None):
    """
    Use this tool to RESCHEDULE or RENAME an event.
    Args:
        event_id: The ID of the event to change.
        new_start_time: (Optional) New start time ISO format.
        new_summary: (Optional) New title.
    """
    try:
        service = get_calendar_service()
        
        # Get existing event
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
        
        if new_summary:
            event['summary'] = new_summary

        if new_start_time:
            # Parse new time with Paris Timezone
            dt_naive = datetime.datetime.fromisoformat(new_start_time.replace("Z", ""))
            start_dt_paris = dt_naive.replace(tzinfo=PARIS_TZ)
            
            # Keep original duration if possible, else default to 1h
            duration = datetime.timedelta(hours=1)
            if 'start' in event and 'dateTime' in event['start'] and 'end' in event:
                old_start = datetime.datetime.fromisoformat(event['start']['dateTime'])
                old_end = datetime.datetime.fromisoformat(event['end']['dateTime'])
                duration = old_end - old_start
            
            end_dt_paris = start_dt_paris + duration
            
            event['start'] = {'dateTime': start_dt_paris.isoformat(), 'timeZone': 'Europe/Paris'}
            event['end'] = {'dateTime': end_dt_paris.isoformat(), 'timeZone': 'Europe/Paris'}

        updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()
        return f"SUCCESS! Event updated to: {updated_event.get('start').get('dateTime')} - {updated_event.get('summary')}"

    except Exception as e:
        return f"Failed to update event: {str(e)}"