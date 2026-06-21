# How MindVault Works - Complete Technical Walkthrough

This guide explains the entire architecture and data flow of MindVault from the ground up.

## Part 1: FastAPI Fundamentals

### What is FastAPI?

FastAPI is a modern Python web framework for building APIs. Think of it as a way to create HTTP endpoints that clients can call.

**Key Concepts:**

1. **Routes/Endpoints**: URLs that accept HTTP requests (GET, POST, etc.)
2. **Request Handlers**: Python functions that process requests
3. **Automatic Validation**: FastAPI validates request data using Python type hints
4. **Middleware**: Code that runs before/after requests (like CORS)

### The Main Application File

Let's break down [main.py](../backend/app/main.py):

```python
# 1. Create the FastAPI application instance
app = FastAPI(title="MindVault API", version="1.0.0")
```
This creates your web server. Everything hangs off this `app` object.

```python
# 2. Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
```
**Why?** Browsers block requests from one origin (localhost:5173) to another (localhost:8000) by default. CORS middleware tells the browser "it's okay, these origins can talk to each other."

```python
# 3. Create shared storage
pdf_storage = {}
```
This is a simple Python dictionary that stores uploaded PDF text. Key = document_id, Value = extracted text.

```python
# 4. Register routers
app.include_router(upload.router)
app.include_router(chat.router)
```
This tells FastAPI "hey, there are more endpoints defined in upload.py and chat.py - add them to the app."

```python
# 5. Define a route
@app.get("/")
def health():
    return {"status": "MindVault backend running"}
```
- `@app.get("/")` is a **decorator** that registers this function as a handler for GET requests to "/"
- When someone visits `http://localhost:8000/`, this function runs
- FastAPI automatically converts the Python dict to JSON

---

## Part 2: The PDF Upload Flow

Let's trace what happens when a user uploads a PDF.

### Step 1: User Clicks Upload

Frontend sends a request:
```
POST http://localhost:8000/api/upload
Content-Type: multipart/form-data
Body: [PDF file binary data]
```

### Step 2: Request Reaches FastAPI

FastAPI routes the request to [upload.py](../backend/app/api/upload.py):

```python
@router.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
```

**Breaking this down:**

- `@router.post("/api/upload")` - This function handles POST requests to /api/upload
- `response_model=UploadResponse` - FastAPI will validate the response matches this Pydantic model
- `async def` - Asynchronous function (can handle multiple requests efficiently)
- `file: UploadFile = File(...)` - FastAPI extracts the uploaded file from the request
  - `UploadFile` is a FastAPI type that represents an uploaded file
  - `File(...)` means this parameter is required

### Step 3: Validate File Type

```python
if not file.content_type == "application/pdf":
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid file type. Expected PDF, got {file.content_type}"
    )
```

**What happens:**
- Check if the file is a PDF
- If not, raise an HTTPException
- FastAPI catches this and returns a 400 error to the frontend

### Step 4: Read File Content

```python
file_content = await file.read()
```

**Why `await`?**
- Reading files from disk is slow (I/O operation)
- `await` lets other requests be processed while waiting
- This is the benefit of async programming

### Step 5: Validate File Size

```python
validate_pdf_size(len(file_content), max_size_mb=10)
```

This calls a function in [pdf_service.py](../backend/app/services/pdf_service.py):

```python
def validate_pdf_size(file_size: int, max_size_mb: int = 10) -> None:
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise PDFExtractionError(f"PDF file too large. Maximum size is {max_size_mb}MB")
```

**Separation of Concerns:**
- Route handler (upload.py) orchestrates the flow
- Service (pdf_service.py) contains business logic
- This makes code testable and maintainable

### Step 6: Extract Text from PDF

```python
text_content = extract_text_from_pdf(file_content)
```

Let's look at this function in detail:

```python
def extract_text_from_pdf(file_content: bytes) -> str:
    # Create a file-like object from bytes
    pdf_file = io.BytesIO(file_content)
    
    # Read the PDF using pypdf library
    reader = PdfReader(pdf_file)
    
    # Check if PDF has pages
    if len(reader.pages) == 0:
        raise PDFExtractionError("PDF file is empty (no pages)")
    
    # Extract text from all pages
    text_content = []
    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            text_content.append(page_text)
    
    # Join all pages with newlines
    full_text = "\n\n".join(text_content)
    
    return full_text
```

**How pypdf works:**
- PDF files store text in a specific format
- pypdf parses the PDF structure and extracts text objects
- It iterates through each page and combines the text

### Step 7: Generate Document ID

```python
document_id = str(uuid.uuid4())
```

This creates a unique identifier like: `"a3f5b2c1-4d2e-4f9a-8b3c-1e2d3f4a5b6c"`

**Why UUID?**
- Globally unique (virtually impossible to collide)
- Unpredictable (can't guess other document IDs)
- Standard format

### Step 8: Store in Memory

```python
pdf_storage[document_id] = text_content
```

This adds the text to our shared dictionary:
```python
{
    "a3f5b2c1-...": "This is the extracted text from the PDF...",
    "d7h2k4m9-...": "Another document's text..."
}
```

**Why in-memory?**
- **Pros:** Fast, simple, no database setup
- **Cons:** Lost on restart, limited by RAM
- **For MVP:** Perfect. For production (Phase 3), we'll use a database.

### Step 9: Return Response

```python
return UploadResponse(
    status="success",
    document_id=document_id,
    text_length=len(text_content),
    message=f"PDF uploaded successfully. Extracted {len(text_content)} characters."
)
```

FastAPI automatically:
1. Validates the response matches `UploadResponse` schema
2. Converts the Python object to JSON
3. Sends it back to the frontend

**Frontend receives:**
```json
{
  "status": "success",
  "document_id": "a3f5b2c1-...",
  "text_length": 5234,
  "message": "PDF uploaded successfully. Extracted 5234 characters."
}
```

---

## Part 3: The Question Answering Flow

Now let's trace what happens when a user asks a question.

### Step 1: User Types Question

Frontend sends:
```
POST http://localhost:8000/api/ask
Content-Type: application/json
Body: {
  "question": "What is this document about?",
  "document_id": "a3f5b2c1-..."
}
```

### Step 2: Request Reaches FastAPI

FastAPI routes to [chat.py](../backend/app/api/chat.py):

```python
@router.post("/api/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
```

**What's happening:**
- FastAPI receives the JSON body
- It sees the parameter type is `QuestionRequest` (a Pydantic model)
- It automatically:
  1. Parses the JSON
  2. Validates it matches the schema
  3. Creates a `QuestionRequest` object
  4. Passes it to the function

### Step 3: Pydantic Validation

Let's look at the schema in [schemas.py](../backend/app/models/schemas.py):

```python
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask")
    document_id: str = Field(..., description="ID of the uploaded document")
```

**What Pydantic does:**
- Checks `question` is a string with at least 1 character
- Checks `document_id` is a string
- If validation fails, FastAPI returns a 422 error automatically

**Example of failed validation:**
```json
// Request with empty question
{"question": "", "document_id": "abc"}

// FastAPI returns:
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Step 4: Check Document Exists

```python
if request.document_id not in pdf_storage:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document not found. Please upload a PDF first."
    )
```

This looks up the document_id in our storage dictionary. If it's not there, return a 404 error.

### Step 5: Retrieve Document Context

```python
context = pdf_storage[request.document_id]
```

This gets the full extracted text from the PDF. For example:
```
"Chapter 1: Introduction\n\nThis document discusses artificial intelligence and machine learning. AI has become increasingly important..."
```

### Step 6: Call Ollama Service

```python
answer = generate_answer(
    question=request.question,
    context=context
)
```

Now let's dive into [ollama_service.py](../backend/app/services/ollama_service.py):

```python
def generate_answer(question: str, context: str, model: str = "qwen3.5:2b") -> str:
    # Construct the prompt
    prompt = f"""You are a helpful AI assistant. Answer the question based on the provided document context.

Context:
{context[:8000]}

Question: {question}

Answer:"""
```

**Breaking this down:**

1. **Truncate context to 8000 characters**
   - LLMs have token limits
   - 8000 chars ≈ 2000 tokens
   - For MVP, we just use the first 8000 chars
   - In Phase 2 (RAG), we'll intelligently select relevant chunks

2. **Format as a prompt**
   - Give the model clear instructions
   - Provide the context
   - Ask the question
   - The model generates text that follows

### Step 7: Call Ollama API

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

**What happens here:**

1. The `ollama` Python library makes an HTTP request to Ollama (running on localhost:11434)
2. Ollama loads the model (qwen3.5:2b) if not already in memory
3. Ollama runs inference (generates text based on the prompt)
4. Returns the response

**Under the hood:**
```
Python app → HTTP request → Ollama server → Loads model → Runs inference → Returns text
```

### Step 8: Extract Answer

```python
answer = response["message"]["content"]
return answer.strip()
```

The Ollama response looks like:
```python
{
    "model": "qwen3.5:2b",
    "message": {
        "role": "assistant",
        "content": "This document is about artificial intelligence and machine learning, focusing on..."
    }
}
```

We extract just the text content.

### Step 9: Return to Frontend

```python
return AnswerResponse(
    answer=answer,
    document_id=request.document_id,
    question=request.question
)
```

FastAPI converts this to JSON and sends it back:
```json
{
  "answer": "This document is about artificial intelligence...",
  "document_id": "a3f5b2c1-...",
  "question": "What is this document about?"
}
```

---

## Part 4: Architecture Patterns

### 1. Layered Architecture

```
┌─────────────────────────────┐
│   API Layer (upload.py)     │  ← HTTP request/response handling
│   - Validate request         │
│   - Call services            │
│   - Return response          │
└─────────────┬───────────────┘
              │
┌─────────────▼───────────────┐
│   Service Layer              │  ← Business logic
│   - pdf_service.py           │
│   - ollama_service.py        │
│   - Pure Python functions    │
└─────────────┬───────────────┘
              │
┌─────────────▼───────────────┐
│   External Dependencies      │  ← Third-party libraries
│   - pypdf                    │
│   - ollama                   │
└─────────────────────────────┘
```

**Benefits:**
- API layer doesn't know HOW to extract PDF text, just that it CAN
- Services are reusable (could be called from CLI, tests, etc.)
- Easy to test each layer independently

### 2. Dependency Injection

```python
# main.py
pdf_storage = {}
upload.set_pdf_storage(pdf_storage)
chat.set_pdf_storage(pdf_storage)
```

Both routers share the same storage object. This is "dependency injection" - passing dependencies rather than creating them internally.

**Why?**
- Both endpoints can access the same data
- Easy to swap implementations (e.g., replace dict with Redis)
- Testable (can inject a mock storage)

### 3. Error Handling Hierarchy

```
User uploads invalid file
    ↓
HTTPException raised (400)
    ↓
FastAPI catches it
    ↓
Returns JSON error to frontend
    ↓
Frontend shows error message to user
```

**Custom exceptions:**
```python
class PDFExtractionError(Exception):
    """Custom exception for PDF extraction errors"""
    pass
```

These are caught and converted to HTTPExceptions:
```python
try:
    text_content = extract_text_from_pdf(file_content)
except PDFExtractionError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e)
    )
```

---

## Part 5: Complete Data Flow Diagram

```
┌──────────┐
│  Browser │
│  (User)  │
└────┬─────┘
     │
     │ 1. Upload PDF file
     │
┌────▼──────────────────────────────────────────┐
│  Frontend (React)                             │
│  - PdfUpload.tsx captures file                │
│  - Validates client-side (type, size)         │
│  - Calls api.ts → uploadPDF(file)            │
└────┬──────────────────────────────────────────┘
     │
     │ 2. POST /api/upload (multipart/form-data)
     │
┌────▼──────────────────────────────────────────┐
│  FastAPI (Python)                             │
│  ┌──────────────────────────────────────┐    │
│  │ upload.py                             │    │
│  │ - Validate file type                  │    │
│  │ - Read file content                   │    │
│  │ - Validate size                       │    │
│  └──────┬───────────────────────────────┘    │
│         │                                     │
│  ┌──────▼───────────────────────────────┐    │
│  │ pdf_service.py                        │    │
│  │ - Create BytesIO from bytes           │    │
│  │ - Use pypdf to parse PDF structure    │    │
│  │ - Extract text from each page         │    │
│  │ - Combine pages                       │    │
│  └──────┬───────────────────────────────┘    │
│         │                                     │
│  ┌──────▼───────────────────────────────┐    │
│  │ Storage (dict)                        │    │
│  │ document_id → extracted_text          │    │
│  └──────┬───────────────────────────────┘    │
└─────────┼─────────────────────────────────────┘
          │
          │ 3. Return document_id
          │
┌─────────▼─────────────────────────────────────┐
│  Frontend                                     │
│  - Stores document_id in state               │
│  - Shows success message                      │
│  - Enables question input                     │
└─────────┬─────────────────────────────────────┘
          │
          │ 4. User types question
          │
┌─────────▼─────────────────────────────────────┐
│  Frontend                                     │
│  - QuestionInput.tsx captures text            │
│  - Calls api.ts → askQuestion(docId, question)│
└─────────┬─────────────────────────────────────┘
          │
          │ 5. POST /api/ask (JSON)
          │    {question, document_id}
          │
┌─────────▼─────────────────────────────────────┐
│  FastAPI                                      │
│  ┌──────────────────────────────────────┐    │
│  │ chat.py                               │    │
│  │ - Validate request (Pydantic)         │    │
│  │ - Check document exists               │    │
│  │ - Retrieve context from storage       │    │
│  └──────┬───────────────────────────────┘    │
│         │                                     │
│  ┌──────▼───────────────────────────────┐    │
│  │ ollama_service.py                     │    │
│  │ - Construct prompt (context+question) │    │
│  │ - Truncate to 8000 chars              │    │
│  │ - Call ollama.chat()                  │    │
│  └──────┬───────────────────────────────┘    │
└─────────┼─────────────────────────────────────┘
          │
          │ 6. HTTP to Ollama
          │
┌─────────▼─────────────────────────────────────┐
│  Ollama (localhost:11434)                     │
│  - Load model (qwen3.5:2b)                    │
│  - Run inference (LLM generates text)         │
│  - Return generated answer                    │
└─────────┬─────────────────────────────────────┘
          │
          │ 7. Return answer
          │
┌─────────▼─────────────────────────────────────┐
│  FastAPI                                      │
│  - Receive answer from Ollama                 │
│  - Create AnswerResponse object               │
│  - Return JSON to frontend                    │
└─────────┬─────────────────────────────────────┘
          │
          │ 8. Display answer
          │
┌─────────▼─────────────────────────────────────┐
│  Frontend                                     │
│  - AnswerDisplay.tsx renders Q&A             │
│  - User sees the answer                       │
└───────────────────────────────────────────────┘
```

---

## Part 6: Key Takeaways

### FastAPI Magic

1. **Automatic Type Validation**
   ```python
   async def upload_pdf(file: UploadFile = File(...)):
   ```
   FastAPI ensures `file` is actually an uploaded file, or returns 422.

2. **Automatic JSON Conversion**
   ```python
   return {"status": "ok"}
   ```
   Automatically becomes `{"status": "ok"}` JSON response.

3. **Dependency Injection**
   ```python
   file: UploadFile = File(...)
   ```
   FastAPI extracts the file from the request for you.

4. **Auto-Generated Docs**
   Visit http://localhost:8000/docs - FastAPI generates interactive API documentation automatically!

### Architecture Principles

1. **Separation of Concerns**
   - Routes: Handle HTTP
   - Services: Contain logic
   - Models: Define data structures

2. **Single Responsibility**
   - pdf_service: ONLY deals with PDFs
   - ollama_service: ONLY deals with LLM
   - upload.py: ONLY orchestrates upload flow

3. **Fail Fast**
   - Validate at the edge (API layer)
   - Don't process invalid data
   - Clear error messages

### Where to Go Next

**To understand better:**
1. Read the FastAPI tutorial: https://fastapi.tiangolo.com/tutorial/
2. Experiment: Add a new endpoint (e.g., DELETE /api/document/{id})
3. Add logging: Print statements to see the flow
4. Use the interactive docs at http://localhost:8000/docs

**To extend:**
1. Add document listing endpoint
2. Add document deletion
3. Save/load storage from disk (JSON file)
4. Add conversation history

---

## Glossary

- **Endpoint**: A URL that accepts HTTP requests (e.g., POST /api/upload)
- **Route**: Same as endpoint
- **Handler**: The Python function that processes a request
- **Middleware**: Code that runs for every request (e.g., CORS)
- **Pydantic**: Library for data validation using Python type hints
- **Async/Await**: Python syntax for asynchronous programming
- **HTTPException**: FastAPI's way to return error responses
- **Router**: A way to organize related endpoints (upload.router)
- **Dependency Injection**: Passing objects to functions instead of creating them internally
- **Decorator**: `@app.get()` - wraps a function to add behavior
