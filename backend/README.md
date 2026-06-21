# MindVault Backend

FastAPI backend for MindVault AI Knowledge Assistant.

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure Ollama is installed and running:
```bash
# Install Ollama from https://ollama.com
# Pull a model (e.g., llama3.2)
ollama pull llama3.2
```

## Run

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Health check
- `GET /api/health` - Detailed health check with Ollama status
- `POST /api/upload` - Upload a PDF file
- `POST /api/ask` - Ask a question about an uploaded document

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI application
│   ├── api/             # API routes
│   │   ├── upload.py    # PDF upload endpoint
│   │   └── chat.py      # Question answering endpoint
│   ├── services/        # Business logic
│   │   ├── pdf_service.py    # PDF text extraction
│   │   └── ollama_service.py # Ollama LLM integration
│   └── models/          # Data models
│       └── schemas.py   # Pydantic schemas
├── requirements.txt
└── venv/
```
