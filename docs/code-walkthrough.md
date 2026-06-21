# MindVault Code Walkthrough - Line by Line

This document walks through the actual code files with detailed explanations.

## File 1: main.py (Application Entry Point)

**Location:** `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
```
**Import statements:**
- `FastAPI`: The main class to create your web application
- `CORSMiddleware`: Handles Cross-Origin Resource Sharing (lets frontend talk to backend)

---

```python
from app.api import upload, chat
from app.services.ollama_service import check_ollama_health
```
**Import our own modules:**
- `upload`: Contains the PDF upload endpoint
- `chat`: Contains the question answering endpoint
- `check_ollama_health`: Function to verify Ollama is running

---

```python
app = FastAPI(title="MindVault API", version="1.0.0")
```
**Create the application:**
- This is THE central object for your entire API
- `title` appears in the auto-generated docs
- `version` also appears in docs

**What this does:**
- Sets up a web server
- Registers all the routes you'll define
- Handles request/response cycle

---

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
**CORS Configuration:**

Without this, you'd see in browser console:
```
❌ Access to fetch at 'http://localhost:8000/api/upload' from origin 'http://localhost:5173' 
   has been blocked by CORS policy
```

**What each setting means:**
- `allow_origins`: Which frontend URLs can call this API
- `allow_credentials`: Allow cookies/auth headers (not used in MVP, but future-proof)
- `allow_methods`: Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
- `allow_headers`: Allow all headers (Content-Type, Authorization, etc.)

---

```python
pdf_storage = {}
```
**In-Memory Database:**

This simple dictionary stores all uploaded documents:
```python
{
    "uuid-1234": "Full text of document 1...",
    "uuid-5678": "Full text of document 2...",
}
```

**Lifecycle:**
- Created when server starts
- Persists while server is running
- Lost when server stops

**For production:**
- Replace with PostgreSQL/MongoDB
- Or keep in Redis for fast access
- Phase 3 will add persistence

---

```python
upload.set_pdf_storage(pdf_storage)
chat.set_pdf_storage(pdf_storage)
```
**Dependency Injection:**

Both `upload` and `chat` modules need access to storage. We "inject" the same dictionary into both.

**Why not just import pdf_storage directly?**
- Cleaner: Explicit dependencies
- Testable: Can inject a mock storage for tests
- Flexible: Easy to swap storage implementations

**How it works:**
```python
# In upload.py
pdf_storage = {}  # Module-level variable

def set_pdf_storage(storage: dict):
    global pdf_storage
    pdf_storage = storage  # Update the module-level variable
```

---

```python
app.include_router(upload.router)
app.include_router(chat.router)
```
**Register Routes:**

Instead of defining all endpoints in main.py, we organize them into separate files.

`upload.router` contains:
- POST /api/upload

`chat.router` contains:
- POST /api/ask

**This is like saying:**
"Hey FastAPI, go look in upload.py and chat.py for more endpoints to add to the app"

---

```python
@app.get("/")
def health():
    return {"status": "MindVault backend running"}
```
**Basic Health Check:**

`@app.get("/")` is a **decorator** that:
1. Registers the function as a route handler
2. Tells FastAPI this handles GET requests to "/"

**When called:**
```bash
curl http://localhost:8000/
```

**Returns:**
```json
{"status": "MindVault backend running"}
```

**Under the hood:**
1. Request arrives at FastAPI
2. FastAPI routes it to this function
3. Function returns a Python dict
4. FastAPI converts dict to JSON
5. Sends response with Content-Type: application/json

---

```python
@app.get("/api/health")
def api_health():
    ollama_status = check_ollama_health()
    return {
        "status": "ok",
        "message": "API is healthy",
        "ollama": ollama_status,
        "documents_in_memory": len(pdf_storage)
    }
```
**Detailed Health Check:**

Returns:
```json
{
  "status": "ok",
  "message": "API is healthy",
  "ollama": {
    "status": "healthy",
    "ollama_running": true,
    "model_available": true,
    "available_models": ["qwen3.5:2b"]
  },
  "documents_in_memory": 2
}
```

**Use cases:**
- Monitoring: Health check endpoints for uptime monitoring
- Debugging: See if Ollama is connected
- Metrics: How many documents are loaded

---

## File 2: upload.py (PDF Upload Endpoint)

**Location:** `backend/app/api/upload.py`

```python
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status
```

**Imports explained:**
- `uuid`: Generate unique IDs
- `APIRouter`: Create a router (group of related endpoints)
- `UploadFile`: FastAPI type for uploaded files
- `File`: Dependency to extract file from request
- `HTTPException`: Raise HTTP errors
- `status`: HTTP status codes (400, 404, 500, etc.)

---

```python
router = APIRouter(prefix="/api", tags=["upload"])
```

**Create a Router:**
- `prefix="/api"`: All routes in this router start with /api
- `tags=["upload"]`: Groups endpoints in auto-generated docs

So when we write `@router.post("/upload")`, the full path becomes `/api/upload`.

---

```python
pdf_storage = {}

def set_pdf_storage(storage: dict):
    global pdf_storage
    pdf_storage = storage
```

**Module-Level Storage:**

This creates a module-level variable that will be injected from main.py.

`global pdf_storage` lets us modify the module-level variable (otherwise Python would create a local variable).

---

```python
@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
```

**Route Definition:**

`@router.post("/upload")`:
- POST request
- Path is /upload (becomes /api/upload because of router prefix)

`response_model=UploadResponse`:
- FastAPI will validate the response matches this Pydantic model
- Auto-generates response schema in docs

`async def`:
- Asynchronous function
- Can use `await` inside
- Allows handling multiple requests concurrently

`file: UploadFile = File(...)`:
- Parameter named `file`
- Type is `UploadFile` (FastAPI's file upload type)
- `File(...)` tells FastAPI to extract this from form data
- `...` means it's required (will error if missing)

---

```python
if not file.content_type == "application/pdf":
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid file type. Expected PDF, got {file.content_type}"
    )
```

**Validation:**

`file.content_type` is the MIME type from the HTTP request:
- `"application/pdf"` for PDFs
- `"image/png"` for PNGs
- `"text/plain"` for text files

If wrong type, raise an HTTPException:
- `status_code=400`: Bad Request (client error)
- `detail`: Error message shown to user

**What happens:**
1. FastAPI catches the exception
2. Stops executing the function
3. Returns a 400 response:
   ```json
   {
     "detail": "Invalid file type. Expected PDF, got image/png"
   }
   ```

---

```python
file_content = await file.read()
```

**Read File:**

`file.read()` returns a coroutine (async operation).

`await` waits for it to complete and gets the result (bytes).

**Why async?**
```python
# Synchronous (blocks the entire server)
file_content = file.read()  # Server frozen for 100ms

# Asynchronous (server can handle other requests)
file_content = await file.read()  # Server handles other requests during 100ms wait
```

---

```python
validate_pdf_size(len(file_content), max_size_mb=10)
```

**Size Validation:**

`len(file_content)` gets the number of bytes.

Calls a service function:
```python
def validate_pdf_size(file_size: int, max_size_mb: int = 10) -> None:
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise PDFExtractionError(f"PDF file too large. Maximum size is {max_size_mb}MB")
```

**Math:**
- 1 MB = 1024 KB
- 1 KB = 1024 bytes
- 10 MB = 10 * 1024 * 1024 = 10,485,760 bytes

---

```python
text_content = extract_text_from_pdf(file_content)
```

**Extract Text:**

This calls the service function (explained in next section).

Returns a string like:
```
"Chapter 1: Introduction\n\nThis document discusses...\n\nChapter 2: Methods..."
```

---

```python
document_id = str(uuid.uuid4())
```

**Generate UUID:**

`uuid.uuid4()` generates a random UUID:
```python
UUID('a3f5b2c1-4d2e-4f9a-8b3c-1e2d3f4a5b6c')
```

`str()` converts it to a string:
```python
"a3f5b2c1-4d2e-4f9a-8b3c-1e2d3f4a5b6c"
```

**Why UUID?**
- 2^122 possible values (3.4 × 10^38)
- Chance of collision: negligible
- Can't guess other document IDs

---

```python
pdf_storage[document_id] = text_content
```

**Store in Memory:**

Adds to our dictionary:
```python
{
    "a3f5b2c1-4d2e-4f9a-8b3c-1e2d3f4a5b6c": "Full document text..."
}
```

---

```python
return UploadResponse(
    status="success",
    document_id=document_id,
    text_length=len(text_content),
    message=f"PDF uploaded successfully. Extracted {len(text_content)} characters."
)
```

**Return Response:**

Creates a Pydantic model instance. FastAPI automatically:
1. Validates it matches the schema
2. Converts to JSON
3. Sends to client

**Frontend receives:**
```json
{
  "status": "success",
  "document_id": "a3f5b2c1-4d2e-4f9a-8b3c-1e2d3f4a5b6c",
  "text_length": 5234,
  "message": "PDF uploaded successfully. Extracted 5234 characters."
}
```

---

## File 3: pdf_service.py (PDF Processing)

**Location:** `backend/app/services/pdf_service.py`

```python
import io
from typing import Optional
from pypdf import PdfReader
```

**Imports:**
- `io`: Standard library for in-memory file operations
- `typing.Optional`: Type hint for optional values (not used currently, but good practice)
- `pypdf.PdfReader`: The library that parses PDFs

---

```python
class PDFExtractionError(Exception):
    """Custom exception for PDF extraction errors"""
    pass
```

**Custom Exception:**

This lets us differentiate PDF errors from other errors:

```python
try:
    text = extract_text_from_pdf(content)
except PDFExtractionError as e:
    # Handle PDF-specific errors
    print(f"PDF error: {e}")
except Exception as e:
    # Handle other errors
    print(f"Unknown error: {e}")
```

---

```python
def extract_text_from_pdf(file_content: bytes) -> str:
```

**Function Signature:**
- Input: `file_content: bytes` - Raw PDF file data
- Output: `-> str` - Extracted text

---

```python
pdf_file = io.BytesIO(file_content)
```

**Create File-Like Object:**

`file_content` is bytes (raw data in memory):
```python
b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n...'
```

`BytesIO` wraps bytes to make them act like a file:
```python
# Can now do:
pdf_file.read()    # Read data
pdf_file.seek(0)   # Move to start
```

**Why?**
pypdf expects a file-like object (something you can read from), not raw bytes.

---

```python
reader = PdfReader(pdf_file)
```

**Parse PDF:**

pypdf reads the PDF structure:
- Finds the PDF header
- Parses the object tree
- Extracts page objects
- Prepares for text extraction

**PDF structure (simplified):**
```
PDF File
├── Header (%PDF-1.4)
├── Body
│   ├── Page 1 Object
│   ├── Page 2 Object
│   └── Font Objects
└── Cross-Reference Table
```

---

```python
if len(reader.pages) == 0:
    raise PDFExtractionError("PDF file is empty (no pages)")
```

**Validate Pages:**

Some PDFs might be malformed and have no pages. Check and fail early.

---

```python
text_content = []
for page_num, page in enumerate(reader.pages, start=1):
```

**Iterate Pages:**

`reader.pages` is a list of Page objects:
```python
[Page(1), Page(2), Page(3)]
```

`enumerate(..., start=1)` gives us:
```python
(1, Page(1)), (2, Page(2)), (3, Page(3))
```

---

```python
try:
    page_text = page.extract_text()
    if page_text:
        text_content.append(page_text)
except Exception as e:
    print(f"Warning: Failed to extract text from page {page_num}: {e}")
```

**Extract Text Per Page:**

`page.extract_text()` analyzes the page:
1. Finds text objects in the PDF
2. Determines reading order (left-to-right, top-to-bottom)
3. Combines into a string

**Why try/except?**
Some pages might have corrupted text objects. We log the error but continue with other pages.

---

```python
full_text = "\n\n".join(text_content)
```

**Combine Pages:**

```python
text_content = [
    "Page 1 text...",
    "Page 2 text...",
    "Page 3 text..."
]

full_text = "Page 1 text...\n\nPage 2 text...\n\nPage 3 text..."
```

`\n\n` adds two newlines between pages for readability.

---

```python
if not full_text.strip():
    raise PDFExtractionError("No text could be extracted...")
```

**Validate Result:**

`full_text.strip()` removes leading/trailing whitespace.

If empty after stripping, the PDF had no extractable text (might be image-based).

---

## File 4: ollama_service.py (LLM Integration)

**Location:** `backend/app/services/ollama_service.py`

```python
def generate_answer(question: str, context: str, model: str = "qwen3.5:2b") -> str:
```

**Function Signature:**
- `question`: User's question
- `context`: PDF text
- `model`: Which Ollama model to use (default: qwen3.5:2b)
- Returns: Generated answer

---

```python
prompt = f"""You are a helpful AI assistant. Answer the question based on the provided document context.

Context:
{context[:8000]}

Question: {question}

Answer:"""
```

**Construct Prompt:**

`context[:8000]` takes first 8000 characters.

**Why limit context?**
- LLMs have token limits (e.g., 4096 tokens)
- 1 token ≈ 4 characters
- 8000 chars ≈ 2000 tokens
- Leaves room for question and response

**In Phase 2 (RAG):**
Instead of first 8000 chars, we'll:
1. Split document into chunks
2. Find relevant chunks using embeddings
3. Send only relevant chunks

---

```python
response = ollama.chat(
    model=model,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)
```

**Call Ollama API:**

This makes an HTTP request to Ollama (localhost:11434):

```http
POST http://localhost:11434/api/chat
Content-Type: application/json

{
  "model": "qwen3.5:2b",
  "messages": [
    {
      "role": "user",
      "content": "You are a helpful AI assistant..."
    }
  ]
}
```

**Ollama then:**
1. Loads model into memory (if not loaded)
2. Tokenizes the prompt
3. Runs inference (generates text)
4. Returns response

---

```python
answer = response["message"]["content"]
return answer.strip()
```

**Extract Answer:**

Response structure:
```python
{
    "model": "qwen3.5:2b",
    "created_at": "2026-06-21T10:30:00Z",
    "message": {
        "role": "assistant",
        "content": "This document discusses..."
    },
    "done": true
}
```

We extract just the content and remove extra whitespace.

---

## Key Patterns Used

### 1. Dependency Injection
```python
# main.py
storage = {}
upload.set_pdf_storage(storage)

# upload.py
pdf_storage = {}
def set_pdf_storage(storage: dict):
    global pdf_storage
    pdf_storage = storage
```

### 2. Custom Exceptions
```python
class PDFExtractionError(Exception):
    pass

try:
    extract_text_from_pdf(content)
except PDFExtractionError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### 3. Early Returns / Fail Fast
```python
if not file.content_type == "application/pdf":
    raise HTTPException(...)  # Stop here, don't continue

# Only reached if file is valid
text = extract_text_from_pdf(file_content)
```

### 4. Type Hints
```python
def extract_text_from_pdf(file_content: bytes) -> str:
    ...
```
Makes code self-documenting and enables IDE autocomplete.

---

## Next Steps

1. **Add logging:**
   ```python
   import logging
   
   logging.info(f"Uploading PDF: {file.filename}")
   logging.info(f"Extracted {len(text)} characters")
   ```

2. **Add more validation:**
   ```python
   if len(question) > 500:
       raise HTTPException(400, "Question too long")
   ```

3. **Explore the auto-generated docs:**
   http://localhost:8000/docs
   
   Try the "Try it out" buttons to call endpoints directly!

4. **Read the Pydantic models** in `models/schemas.py` to understand data validation

5. **Experiment:** Try breaking things to see the error handling in action!
