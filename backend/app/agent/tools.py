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
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

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

# --- TOOL 1: READ ---
@tool
def list_calendar_events():
    """
    Use this tool to check the user's schedule.
    It returns a list of upcoming events WITH THEIR IDs.
    IMPORTANT: You need the ID to update or delete an event.
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
            event_id = event["id"] # Capture the ID for internal use
            
            # Format: [ID: xxxxx] - Date: Title
            results.append(f"[ID: {event_id}] - {start}: {summary}")
            
        return "\n".join(results)

    except Exception as e:
        return f"Error fetching calendar: {str(e)}"

# --- TOOL 2: CREATE (With Conflict Check) ---
@tool
def create_calendar_event(summary: str, start_time: str, duration_minutes: int = 60):
    """
    Use this tool to BOOK a new meeting or task.
    It automatically checks if the slot is free before booking.
    
    Args:
        summary: The title of the event (e.g., "Deep Work").
        start_time: The start time in ISO format (e.g., "2026-01-25T14:00:00").
        duration_minutes: How long the event lasts (default is 60 minutes).
    """
    try:
        service = get_calendar_service()
        
        # 1. Parse dates and calculate End Time
        start_dt = datetime.datetime.fromisoformat(start_time)
        end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
        
        # 2. CONFLICT CHECK: Look for events in this specific window
        # We query Google to see if anything exists between start_dt and end_dt
        conflicts_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_dt.isoformat() + "Z", # Convert to UTC string for API
            timeMax=end_dt.isoformat() + "Z",
            singleEvents=True
        ).execute()
        
        conflicts = conflicts_result.get("items", [])
        
        # 3. If conflicts exist, STOP and return error
        if conflicts:
            conflict_summary = conflicts[0]['summary']
            return f"FAILED: Time slot is already booked! There is a conflict with event: '{conflict_summary}'. Ask the user for a different time."

        # 4. If slot is free, proceed with booking
        event_body = {
            'summary': summary,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Europe/Paris', # Force Paris Timezone
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

# --- TOOL 3: DELETE ---
@tool
def delete_calendar_event(event_id: str):
    """
    Use this tool to CANCEL or DELETE an event.
    You must provide the 'event_id' found using 'list_calendar_events'.
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        return "Success! Event deleted."
    except Exception as e:
        return f"Failed to delete event: {str(e)}"

# --- TOOL 4: UPDATE ---
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
            start_dt = datetime.datetime.fromisoformat(new_start_time)
            # Try to keep original duration
            duration = datetime.timedelta(hours=1)
            if 'start' in event and 'dateTime' in event['start'] and 'end' in event:
                old_start = datetime.datetime.fromisoformat(event['start']['dateTime'])
                old_end = datetime.datetime.fromisoformat(event['end']['dateTime'])
                duration = old_end - old_start
            
            end_dt = start_dt + duration
            
            event['start'] = {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Paris'}
            event['end'] = {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Paris'}

        updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()
        return f"Success! Event updated to: {updated_event.get('start').get('dateTime')} - {updated_event.get('summary')}"

    except Exception as e:
        return f"Failed to update event: {str(e)}"