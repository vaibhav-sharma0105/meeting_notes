
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import datetime
from pydantic import BaseModel
from typing import List, Optional

# For local dev, allow HTTP
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

router = APIRouter(prefix="/google", tags=["google"])

# In-memory store for tokens (Use DB in production!)
user_tokens = {}

# Scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly']

class CalendarEvent(BaseModel):
    id: str
    summary: str
    start: str # ISO format
    end: str
    link: Optional[str] = None

@router.get("/login")
def login(request: Request):
    """
    Initiates the OAuth2 flow.
    Requires 'credentials.json' (Client Secret) to be present in backend/.
    """
    # Robust path finding for credentials.json
    possible_paths = [
        "credentials.json",
        os.path.join("backend", "credentials.json"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "credentials.json")
    ]

    creds_path = None
    for p in possible_paths:
        if os.path.exists(p):
            creds_path = p
            break

    if not creds_path:
        # Return 400 or 404 to indicate client configuration error, not server crash
        raise HTTPException(status_code=400, detail="Missing credentials.json. Please place it in the backend folder.")

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        creds_path,
        scopes=SCOPES
    )
    flow.redirect_uri = "http://localhost:8000/google/callback"

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return {"auth_url": authorization_url}

@router.get("/callback")
def callback(state: str, code: str, request: Request):
    """
    Handles the callback from Google.
    """
    try:
        # Re-find path (copy logic for now, could be utility)
        possible_paths = [
            "credentials.json",
            os.path.join("backend", "credentials.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "credentials.json")
        ]
        creds_path = next((p for p in possible_paths if os.path.exists(p)), "credentials.json")

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            creds_path,
            scopes=SCOPES,
            state=state
        )
        flow.redirect_uri = "http://localhost:8000/google/callback"

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Store in memory (keyed by a simple 'user' for single-user MVP)
        user_tokens['default'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        # Redirect back to frontend
        return RedirectResponse("http://localhost:3000?google_connected=true")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events", response_model=List[CalendarEvent])
def get_events():
    """
    Fetches the next 10 events from the user's primary calendar.
    """
    if 'default' not in user_tokens:
        raise HTTPException(status_code=401, detail="User not authenticated with Google")

    token_info = user_tokens['default']
    from google.oauth2.credentials import Credentials

    creds = Credentials(
        token=token_info['token'],
        refresh_token=token_info['refresh_token'],
        token_uri=token_info['token_uri'],
        client_id=token_info['client_id'],
        client_secret=token_info['client_secret'],
        scopes=token_info['scopes']
    )

    try:
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        result = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            result.append(CalendarEvent(
                id=event['id'],
                summary=event.get('summary', 'No Title'),
                start=start,
                end=end,
                link=event.get('htmlLink')
            ))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
