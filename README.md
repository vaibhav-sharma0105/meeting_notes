# MeetOps

An AI-Driven Meeting Intelligence Platform. Ingest Zoom transcripts, generate insights using LLMs (local or cloud), and build a queryable knowledge base.

## Features
- **Flexible Ingestion:** Upload Zoom VTT, Text files (.txt), or JSON summaries.
- **AI Task Extraction:** Automatically extracts Action Items, Assignees, and Due Dates using LiteLLM.
- **Task Management:** Built-in todo list with strike-through completion.
- **Privacy-First Intelligence:** Use LiteLLM to connect to any model (OpenAI, Anthropic, or Local/Ollama).
- **Project Clustering:** Automatically groups meetings into "Projects" based on semantic similarity.
- **Google Calendar Integration:** Connect your Google account to link notes to calendar events.
- **Runtime Configuration:** Switch models and providers directly from the UI without restarting.

## Prerequisites
- Docker & Docker Compose (Recommended)
- OR
- Python 3.11+
- Node.js 18+
- PostgreSQL (with `pgvector` extension installed)

## Quick Start (Docker)

1. **Configure Environment**
   - Copy `backend/config.yaml.example` to `backend/config.yaml` and set your LLM credentials.
   - (Optional) Place `credentials.json` (Google OAuth Client Secret) in `backend/` for Calendar integration.

2. **Run**
   ```bash
   docker-compose up --build
   ```

3. **Access**
   - Frontend: `http://localhost:3000`
   - Backend API Docs: `http://localhost:8000/docs`

## Local Development Setup

If you prefer running the Frontend and Backend locally (not in Docker), you **must still run the Database via Docker** unless you have a local Postgres instance with `pgvector` installed.

### 1. Start Database
**Windows:**
Double-click `start_db.bat`.

**Mac/Linux:**
```bash
./start_db.sh
```

### 2. Backend

1. Navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run Server:
   ```bash
   # Must be run from inside the backend directory for imports to work
   uvicorn main:app --reload
   ```

### 3. Frontend

1. Navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run Development Server:
   ```bash
   npm run dev
   ```

## Configuration & Settings

MeetOps supports dynamic configuration of the LLM provider via the **Settings UI**.

1. **Access Settings:** Click the gear icon in the top-right corner or press `Cmd+K` and search for "Settings".
2. **Configure Provider:**
   - **Base URL:** Enter the API endpoint (e.g., `https://api.openai.com/v1`, `http://localhost:11434` for Ollama, or a custom proxy).
   - **API Key:** Enter your key (stored securely in `config.yaml` on the backend).
3. **Fetch Models:** Click the refresh icon next to the Model dropdown. The system will query the provider and populate the list of available models.
4. **Google Calendar:** Click "Connect Google Calendar" in settings to authorize access. Requires `backend/credentials.json` from GCP Console (OAuth 2.0 Client ID for Web Application).

## Resetting Local Environment

If you encounter dependency issues or need to start fresh:

1. **Docker:**
   ```bash
   docker-compose down -v --rmi all
   docker-compose up --build
   ```

2. **Local Python:**
   ```bash
   # In backend/
   rm -rf venv __pycache__
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
