import os.path
import os
from dotenv import load_dotenv
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Si on modifie ces scopes, il faut supprimer le fichier token.json
SCOPES = ["https://www.googleapis.com/auth/calendar"]

load_dotenv()

CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")   

def main():
    creds = None
    # Le fichier token.json stocke les jetons d'accès et d'actualisation de l'utilisateur.
    # Il est créé automatiquement lors de la première exécution du flux d'autorisation.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # Si il n'y a pas de credentials valides (ou pas du tout), on demande à l'utilisateur de se connecter.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # C'est ici qu'on utilise ton fichier credentials.json
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # On sauvegarde les credentials pour la prochaine fois
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Appel de l'API Calendar : Récupérer les 10 prochains événements
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indique UTC time
        print("🔍 Tentative de récupération des événements...")
        
        events_result = (
            service.events()
            .list(
                calendarId=CALENDAR_ID, 
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("✅ Connexion réussie, mais aucun événement trouvé prochainement.")
        else:
            print("✅ Connexion réussie ! Voici tes 10 prochains événements :")
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(f"- {start}: {event['summary']}")

    except HttpError as error:
        print(f"❌ Une erreur est survenue : {error}")

if __name__ == "__main__":
    main()