# MindVault Architecture

## Phase 1 MVP Architecture

### Overview

MindVault Phase 1 is a simple yet production-ready AI knowledge assistant that allows users to upload PDF documents and ask questions about them using local LLM models.

```
┌─────────────┐
│   Browser   │
│  (Client)   │
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼──────────────────────────────┐
│     React Frontend (Vite)           │
│  - Upload PDF component             │
│  - Question input                   │
│  - Answer display                   │
└──────┬──────────────────────────────┘
       │ Axios
       │ POST /api/upload
       │ POST /api/ask
┌──────▼──────────────────────────────┐
│     FastAPI Backend                 │
│  - CORS middleware                  │
│  - Upload endpoint                  │
│  - Chat endpoint                    │
└──────┬──────────────────────────────┘
       │
       ├─────────────┬─────────────────┐
       │             │                 │
┌──────▼──────┐ ┌───▼────────┐ ┌─────▼─────┐
│ PDF Service │ │ In-Memory  │ │  Ollama   │
│  (pypdf)    │ │  Storage   │ │  Service  │
└─────────────┘ └────────────┘ └─────┬─────┘
                                      │
                              ┌───────▼────────┐
                              │ Ollama Runtime │
                              │  (qwen3.5:2b)  │
                              └────────────────┘
```

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app entry point, CORS config
│   ├── api/             # API route handlers
│   │   ├── upload.py    # PDF upload endpoint
│   │   └── chat.py      # Question answering endpoint
│   ├── services/        # Business logic layer
│   │   ├── pdf_service.py    # PDF text extraction
│   │   └── ollama_service.py # Ollama LLM integration
│   └── models/          # Data models
│       └── schemas.py   # Pydantic request/response models
└── requirements.txt
```

### Design Patterns

**Separation of Concerns:**
- **Routes (api/)**: Handle HTTP requests/responses only
- **Services (services/)**: Contain business logic
- **Models (models/)**: Define data structures and validation

**Error Handling:**
- Custom exceptions per service (PDFExtractionError, OllamaServiceError)
- HTTP exceptions with proper status codes
- User-friendly error messages

### Data Flow

1. **PDF Upload Flow:**
   ```
   Client → upload.py → pdf_service.extract_text_from_pdf()
   → Generate UUID → Store in memory dict → Return document_id
   ```

2. **Question Answering Flow:**
   ```
   Client → chat.py → Retrieve context from memory
   → ollama_service.generate_answer() → Ollama API
   → Return answer to client
   ```

### In-Memory Storage

Simple dictionary structure:
```python
pdf_storage = {
    "document_id_1": "full_extracted_text...",
    "document_id_2": "another_document_text..."
}
```

**Trade-offs:**
- ✅ Simple, no database setup needed
- ✅ Fast access
- ❌ Data lost on restart
- ❌ Not suitable for production (Phase 3 will add persistence)

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── PdfUpload.tsx    # File upload with drag-and-drop
│   │   ├── QuestionInput.tsx # Question form
│   │   └── AnswerDisplay.tsx # Answer rendering
│   ├── services/            # Backend communication
│   │   └── api.ts           # Axios API client
│   ├── types/               # TypeScript definitions
│   │   └── index.ts         # Shared interfaces
│   ├── App.tsx              # Main component
│   ├── App.css              # Styling
│   └── main.tsx             # Entry point
└── package.json
```

### Component Design

**PdfUpload:**
- Handles file selection and drag-and-drop
- Client-side validation (file type, size)
- Calls API service for upload

**QuestionInput:**
- Controlled form input
- Disabled when no document loaded
- Loading state management

**AnswerDisplay:**
- Shows question and answer pair
- Formatted text display

**App (Main):**
- Central state management
- Orchestrates component interactions
- Error handling

### State Management

Simple useState hooks (no Redux needed for MVP):
```typescript
- documentId: string         // Currently loaded document
- fileName: string           // Display name
- currentQuestion: string    // Last asked question
- currentAnswer: string      // LLM response
- isUploading: boolean       // Upload loading state
- isAsking: boolean          // Answer generation state
- error: string              // Error messages
```

## API Specification

### Endpoints

**POST /api/upload**
- **Request:** multipart/form-data with PDF file
- **Response:** `UploadResponse`
  ```json
  {
    "status": "success",
    "document_id": "uuid",
    "text_length": 12345,
    "message": "PDF uploaded successfully..."
  }
  ```

**POST /api/ask**
- **Request:** `QuestionRequest`
  ```json
  {
    "question": "What is this document about?",
    "document_id": "uuid"
  }
  ```
- **Response:** `AnswerResponse`
  ```json
  {
    "answer": "This document is about...",
    "document_id": "uuid",
    "question": "What is this document about?"
  }
  ```

**GET /api/health**
- **Response:** Health status with Ollama connectivity

## Technology Choices

### Why FastAPI?
- Modern Python web framework
- Automatic API documentation (OpenAPI)
- Built-in request validation (Pydantic)
- Async support for future streaming

### Why pypdf?
- Pure Python, no external dependencies
- Simple API for text extraction
- Adequate for MVP (will add more robust extraction in Phase 2)

### Why Ollama?
- Local LLM execution (privacy, no API costs)
- Easy model management
- Good performance with quantized models
- Simple Python client

### Why React + TypeScript?
- Strong typing reduces bugs
- Modern component-based architecture
- Large ecosystem
- Good developer experience

### Why Vite?
- Fast development server
- Hot module replacement
- Modern build tool
- Better than Create React App

## Security Considerations

**Current (MVP):**
- File size validation (10MB limit)
- File type validation (PDF only)
- CORS restricted to localhost:5173

**Future (Phase 3+):**
- User authentication
- Rate limiting
- Input sanitization
- File scanning
- HTTPS only

## Performance Considerations

**Current:**
- Entire PDF sent to LLM (limited to 8000 chars)
- Synchronous request/response
- In-memory storage (fast but limited)

**Future Improvements (Phase 2+):**
- Document chunking
- Semantic search (only send relevant chunks)
- Streaming responses
- Database persistence
- Caching

## Scalability Path

**Phase 1 (Current):** Single user, local deployment
**Phase 2:** Add RAG for better answers
**Phase 3:** Multi-user with database
**Phase 4:** Cloud deployment, horizontal scaling
**Phase 5:** Advanced features (agents, citations, etc.)

## Development Philosophy

1. **Start Simple:** Working MVP before optimization
2. **Clean Architecture:** Proper separation of concerns
3. **Production Patterns:** Even MVP uses good practices
4. **Incremental:** Each phase adds value
5. **Local First:** Privacy and cost benefits
