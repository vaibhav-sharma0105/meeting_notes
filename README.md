# MeetOps

An AI-Driven Meeting Intelligence Platform. Ingest Zoom transcripts, generate insights using LLMs (local or cloud), and build a queryable knowledge base.

## Features
- **Hybrid Ingestion:** Upload Zoom VTT transcripts or Text/JSON summaries.
- **Privacy-First Intelligence:** Use LiteLLM to connect to any model (OpenAI, Anthropic, or Local/Ollama).
- **Project Clustering:** Automatically groups meetings into "Projects" based on semantic similarity.
- **Linear-Style UI:** Modern, high-performance dashboard with Bento Grid layout and Command Palette.
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

2. **Run**
   ```bash
   docker-compose up --build
   ```

3. **Access**
   - Frontend: `http://localhost:3000`
   - Backend API Docs: `http://localhost:8000/docs`

## Local Development Setup

### Backend

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

### Frontend

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
4. **Save:** Clicking "Save changes" updates the backend configuration immediately.

### Manual Configuration
You can also manually edit `backend/config.yaml`:

```yaml
selected_model: "gpt-4o"
models:
  gpt-4o:
    model: "openai/gpt-4o"
    api_key: "os.environ/OPENAI_API_KEY"
  local-llama:
    model: "ollama/llama3"
    api_base: "http://localhost:11434"
```
