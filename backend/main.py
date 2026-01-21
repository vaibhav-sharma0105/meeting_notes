from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_session, create_db_and_tables, engine
from models import Meeting, TranscriptChunk, Task, Project
from services.ingestion import parse_vtt, parse_summary
from services.extraction import extract_action_items
from routers import settings as settings_router
from routers import tasks as tasks_router
from routers import calendar as calendar_router
# from services.intelligence import generate_embedding # Commented out to avoid crash without API Key

app = FastAPI(title="MeetOps API")

app.include_router(settings_router.router)
app.include_router(tasks_router.router)
app.include_router(calendar_router.router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # In a real app, use Alembic. For MVP, this is fine.
    # It might fail if DB is not reachable, so we wrap in try/except for local dev robustness
    try:
        create_db_and_tables()
    except Exception as e:
        print(f"Warning: Could not connect to database at startup. {e}")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "MeetOps Backend Running"}

@app.post("/upload")
async def upload_meeting(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    content = await file.read()
    # Decode safely, ignoring errors or replacing them if UTF-8 fails (common in Windows text files)
    try:
        content_str = content.decode("utf-8")
    except UnicodeDecodeError:
        # Fallback to latin-1 or similar if utf-8 fails, or ignore
        content_str = content.decode("utf-8", errors="replace")

    file_ext = "vtt"
    if file.filename.endswith(".vtt"):
        file_ext = "vtt"
    elif file.filename.endswith(".txt"):
        file_ext = "txt"
    else:
        file_ext = "json"

    meeting = Meeting(
        title=file.filename,
        source_filename=file.filename,
        file_type=file_ext,
        status="processing"
    )
    session.add(meeting)
    session.commit()
    session.refresh(meeting)

    # Process synchronously for MVP (should be background task)
    try:
        if meeting.file_type == "vtt":
            chunks_data = parse_vtt(content_str)
            full_text = ""
            for c in chunks_data:
                full_text += f"{c['speaker']}: {c['text']}\n"
                chunk = TranscriptChunk(
                    meeting_id=meeting.id,
                    start_time=c['start_time'],
                    end_time=c['end_time'],
                    speaker=c['speaker'],
                    text=c['text'],
                    # embedding=generate_embedding(c['text']) # cost money, skip for now
                )
                session.add(chunk)

            # Try to extract tasks from transcript too
            extracted_tasks = extract_action_items(full_text)
            for t in extracted_tasks:
                 task = Task(
                     meeting_id=meeting.id,
                     description=t.get('description'),
                     assignee=t.get('assignee'),
                     status="todo"
                 )
                 session.add(task)

        else:
            # Summary (JSON or TXT)
            data = parse_summary(content_str, meeting.file_type)
            meeting.summary_text = str(data)

            # Extract tasks
            text_to_analyze = ""
            if "raw_text" in data:
                text_to_analyze = data["raw_text"]
            else:
                text_to_analyze = json.dumps(data)

            extracted_tasks = extract_action_items(text_to_analyze)
            for t in extracted_tasks:
                 task = Task(
                     meeting_id=meeting.id,
                     description=t.get('description'),
                     assignee=t.get('assignee'),
                     status="todo"
                 )
                 session.add(task)

        meeting.status = "completed"
        session.add(meeting)
        session.commit()
    except Exception as e:
        meeting.status = "failed"
        session.add(meeting)
        session.commit()
        raise HTTPException(status_code=500, detail=str(e))

    return {"meeting_id": meeting.id, "status": "completed"}

@app.get("/dashboard")
def get_dashboard_data(session: Session = Depends(get_session)):
    """
    Returns data formatted for the Bento Grid.
    """
    # 1. Daily Focus (Most recent meeting)
    statement = select(Meeting).order_by(Meeting.date.desc()).limit(1)
    recent = session.exec(statement).first()

    # 2. Incoming (Unprocessed or recent)
    statement_incoming = select(Meeting).order_by(Meeting.date.desc()).limit(5)
    incoming = session.exec(statement_incoming).all()

    return {
        "daily_focus": recent,
        "incoming": incoming,
        "sentiment": [ # Mock data for sparkline
            {"day": "Mon", "value": 0.8},
            {"day": "Tue", "value": 0.6},
            {"day": "Wed", "value": 0.9},
            {"day": "Thu", "value": 0.7},
            {"day": "Fri", "value": 0.85},
        ],
        "top_project": {
            "name": "Q3 Roadmap",
            "meeting_count": 12,
            "last_active": "2 hours ago"
        }
    }

@app.get("/search")
def search_knowledge(query: str, session: Session = Depends(get_session)):
    # Vector search would go here
    # For MVP, simple text search on chunks
    statement = select(TranscriptChunk).where(TranscriptChunk.text.contains(query)).limit(10)
    results = session.exec(statement).all()
    return results
