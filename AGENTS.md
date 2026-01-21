# MeetOps: AI-Driven Meeting Intelligence Platform

## 1. Project Overview
MeetOps is a privacy-first application designed to ingest Zoom transcripts/summaries, leverage LLMs via LiteLLM for semantic processing, and integrate with Google Calendar to create a consolidated, queryable knowledge base.

## 2. Tech Stack & Architecture (Strict)
*   **Backend:** Python 3.11+ using FastAPI.
*   **LLM Interface:** `litellm` library. MUST support configuration via `config.yaml` for: `api_key`, `model_name`, and `api_base` (Base URL).
*   **Database:** PostgreSQL with `pgvector` extension. ORM: `SQLModel`.
*   **Ingestion:** `webvtt-py` for .vtt files; custom parsing for .txt/.json summaries.
*   **Frontend:** Next.js 14+ (App Router), TypeScript.
*   **UI Library:** Shadcn/UI (Radix Primitives).
*   **Styling:** Tailwind CSS (Zinc color palette for "Linear-style" dark mode).
*   **State Management:** TanStack Query (React Query).
*   **Layout:** "Bento Grid" using CSS Grid.
*   **Navigation:** Command Palette using `cmdk`.

## 3. Coding Standards
*   **Python:**
    *   All functions must have type hints.
    *   Use Pydantic models (SQLModel) for data validation.
    *   Strict separation of concerns: `models`, `services`, `api`.
*   **TypeScript/React:**
    *   Use Functional Components.
    *   Strict typing (no `any`).
    *   Use Server Components by default, Client Components (`"use client"`) only for interactivity.
    *   Prioritize "Optimistic UI" updates.
*   **General:**
    *   Code must be clean, readable, and well-documented.
    *   Secrets must never be hardcoded; use environment variables or config files.

## 4. Directory Structure
```
/
├── backend/
│   ├── core/           # Config, logging
│   ├── models.py       # SQLModel schemas
│   ├── services/       # Logic (Ingestion, RAG, Clustering)
│   ├── main.py         # FastAPI entrypoint
│   └── requirements.txt
├── frontend/
│   ├── app/            # Next.js App Router
│   ├── components/     # UI Components (Shadcn, Custom)
│   ├── lib/            # Utilities, API hooks
│   └── public/
├── docker-compose.yml
└── README.md
```

## 5. Architectural Patterns
*   **Privacy-First:** Support local LLMs (Ollama) via `litellm` base_url.
*   **Bento Grid:** The dashboard is a modular grid.
*   **Hybrid Ingestion:** Handle both detailed VTT transcripts and high-level summaries.
*   **Clustering:** Use embedding-based clustering to identify "Projects" without manual tagging.
