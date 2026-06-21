# MindVault AI - Claude Code Instructions

## Project Overview

MindVault is an AI Knowledge Assistant.

The goal is to build a production-style GenAI application where users can upload documents and interact with their knowledge using AI.

The project should evolve gradually:

1. MVP with local LLM
2. RAG-based knowledge assistant
3. Multi-document AI workspace
4. Cloud deployment on AWS


## Current Phase

We are currently building Phase 1: MVP.

The goal:

Create a complete end-to-end application.

User flow:

User
↓
React Frontend
↓
FastAPI Backend
↓
Upload PDF
↓
Extract document text
↓
Send context + question to Ollama
↓
Generate AI response
↓
Display answer in UI


## Tech Stack

Frontend:
- React
- TypeScript
- Vite

Backend:
- Python
- FastAPI

AI:
- Ollama
- Local LLM models (Llama/Qwen)

Future:
- Embedding models
- Vector database
- RAG


## Architecture Guidelines

Follow a clean separation of concerns.

Frontend:

frontend/
- components
- pages
- services
- hooks


Backend:

backend/
app/
    main.py

    api/
        upload.py
        chat.py

    services/
        pdf_service.py
        ollama_service.py


API routes should not contain business logic.

Business logic belongs inside services.


## Development Rules

- Build incrementally.
- Do not add unnecessary dependencies.
- Prefer simple solutions first.
- Explain architectural decisions.
- Before implementing major features, provide a short plan.
- Keep code production-quality.
- Avoid premature optimization.


## Current Restrictions

Do not implement yet:

- Authentication
- User management
- AWS deployment
- Vector database
- RAG pipeline
- Agents


## Future Architecture

The application will eventually become:

Document
↓
Text extraction
↓
Chunking
↓
Embeddings
↓
Vector Database
↓
Retrieval
↓
LLM
↓
Answer


## First Milestone

Complete:

- React application setup
- FastAPI application setup
- PDF upload API
- PDF text extraction
- Ollama integration
- Chat interface
- End-to-end question answering


## Important

Before making changes:

1. Inspect the existing repository.
2. Understand the current state.
3. Suggest an implementation plan.
4. Then modify files.