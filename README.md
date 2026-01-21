# MeetOps

An AI-Driven Meeting Intelligence Platform. Ingest Zoom transcripts, generate insights using LLMs (local or cloud), and build a queryable knowledge base.

## Features
- **Hybrid Ingestion:** Upload Zoom VTT transcripts or Text/JSON summaries.
- **Privacy-First Intelligence:** Use LiteLLM to connect to any model (OpenAI, Anthropic, or Local/Ollama).
- **Project Clustering:** Automatically groups meetings into "Projects" based on semantic similarity.
- **Linear-Style UI:** Modern, high-performance dashboard with Bento Grid layout and Command Palette.

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
4. Configure `config.yaml`:
   - Set up your model provider (e.g., OpenAI API Key or Local LLM Base URL).
5. Run Server:
   ```bash
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

## Configuration (LiteLLM)
Edit `backend/config.yaml` to define your models:

```yaml
model_name: "gpt-4o"
litellm_params:
  model: "openai/gpt-4o"
  api_key: "os.environ/OPENAI_API_KEY"
  # For local:
  # api_base: "http://localhost:11434"
```
