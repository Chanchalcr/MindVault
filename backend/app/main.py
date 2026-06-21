from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import upload, chat
from app.services.ollama_service import check_ollama_health

app = FastAPI(title="MindVault API", version="1.0.0")

# CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for uploaded PDF content
# Format: {document_id: text_content}
pdf_storage = {}

# Inject pdf_storage into API routers
upload.set_pdf_storage(pdf_storage)
chat.set_pdf_storage(pdf_storage)

# Register routers
app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/")
def health():
    return {"status": "MindVault backend running"}


@app.get("/api/health")
def api_health():
    """API health check including Ollama status"""
    ollama_status = check_ollama_health()
    return {
        "status": "ok",
        "message": "API is healthy",
        "ollama": ollama_status,
        "documents_in_memory": len(pdf_storage)
    }
