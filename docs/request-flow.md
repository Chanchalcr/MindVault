# Request Flow - Step by Step Examples

This document shows **exactly** what happens at each step when you use MindVault.

## Example 1: Uploading a PDF

### User Action
User drags `resume.pdf` onto the upload area and drops it.

---

### Step 1: Frontend Capture

**File:** `frontend/src/components/PdfUpload.tsx`

```typescript
const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFile(e.dataTransfer.files[0]);
    }
}
```

**What happens:**
- Browser's drag-and-drop API captures the file
- `e.dataTransfer.files[0]` gets the File object
- File object contains:
  ```javascript
  {
      name: "resume.pdf",
      size: 245670,  // bytes
      type: "application/pdf",
      lastModified: 1719000000000
  }
  ```

---

### Step 2: Client-Side Validation

```typescript
const handleFile = async (file: File) => {
    // Validate type
    if (file.type !== 'application/pdf') {
        setError('Please upload a PDF file');
        return;
    }
    
    // Validate size (10MB = 10 * 1024 * 1024 bytes)
    if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
    }
    
    // Proceed to upload
    setIsLoading(true);
    const response = await uploadPDF(file);
}
```

**Why validate on client?**
- Faster feedback (no network round-trip)
- Saves bandwidth (don't send invalid files)
- Better UX (immediate error messages)

**But also validate on server:**
- Client validation can be bypassed
- Server is the source of truth

---

### Step 3: API Call

**File:** `frontend/src/services/api.ts`

```typescript
export const uploadPDF = async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post<UploadResponse>('/api/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    
    return response.data;
};
```

**What FormData does:**

Creates multipart form data:
```
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="resume.pdf"
Content-Type: application/pdf

%PDF-1.4
%âãÏÓ
[binary PDF data...]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

---

### Step 4: HTTP Request

**Actual HTTP request sent:**

```http
POST http://localhost:8000/api/upload HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 245670
Origin: http://localhost:5173

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="resume.pdf"
Content-Type: application/pdf

[245,670 bytes of PDF data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

---

### Step 5: FastAPI Receives Request

**File:** `backend/app/main.py`

FastAPI's request handling:

1. **Check CORS:**
   ```python
   # CORSMiddleware runs
   origin = request.headers.get("Origin")  # "http://localhost:5173"
   if origin in allow_origins:
       # Add CORS headers to response
       response.headers["Access-Control-Allow-Origin"] = origin
   ```

2. **Route to handler:**
   ```python
   # FastAPI router finds: POST /api/upload
   # Routes to: upload.upload_pdf()
   ```

3. **Extract parameters:**
   ```python
   # FastAPI sees: file: UploadFile = File(...)
   # Parses multipart form data
   # Creates UploadFile object
   ```

---

### Step 6: Request Handler

**File:** `backend/app/api/upload.py`

```python
async def upload_pdf(file: UploadFile = File(...)):
    # file is now:
    # UploadFile(
    #     filename="resume.pdf",
    #     content_type="application/pdf",
    #     file=<SpooledTemporaryFile>
    # )
```

---

### Step 7: Validation

```python
# Check content type
if not file.content_type == "application/pdf":
    raise HTTPException(...)  # Would stop here if wrong type
```

**File passed validation ✓**

---

### Step 8: Read File

```python
file_content = await file.read()
# file_content is now bytes:
# b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog...'
# Length: 245670 bytes
```

**Why `await`?**

Timeline without await:
```
Request 1: [----Read File (100ms)----][Process]
Request 2:                              [----Read File----][Process]
Total: 200ms for 2 requests
```

Timeline with await:
```
Request 1: [Read File (async)]         [Process]
Request 2:  [Read File (async)]        [Process]
Total: 100ms for 2 requests (parallel)
```

---

### Step 9: Size Validation

```python
validate_pdf_size(len(file_content), max_size_mb=10)
# len(file_content) = 245670 bytes
# 245670 < 10,485,760 ✓ Valid
```

---

### Step 10: Extract Text

**File:** `backend/app/services/pdf_service.py`

```python
text_content = extract_text_from_pdf(file_content)
```

**Inside the function:**

```python
# 1. Create file-like object
pdf_file = io.BytesIO(file_content)

# 2. Parse PDF
reader = PdfReader(pdf_file)
# pypdf analyzes the PDF structure:
# - Reads header: %PDF-1.4
# - Parses object tree
# - Finds 3 pages

# 3. Extract text from each page
text_content = []

# Page 1:
page_text = reader.pages[0].extract_text()
# Returns: "John Doe\nSoftware Engineer\n\nExperience:\n..."
text_content.append(page_text)

# Page 2:
page_text = reader.pages[1].extract_text()
# Returns: "Education:\nBS Computer Science\n..."
text_content.append(page_text)

# Page 3:
page_text = reader.pages[2].extract_text()
# Returns: "Skills:\nPython, JavaScript, React..."
text_content.append(page_text)

# 4. Combine
full_text = "\n\n".join(text_content)
# Result: "John Doe\nSoftware Engineer...\n\nEducation:\nBS Computer Science...\n\nSkills:\nPython, JavaScript..."
```

**Final extracted text:**
```
"John Doe
Software Engineer

Experience:
Senior Developer at TechCorp (2020-Present)
- Led team of 5 engineers
- Built microservices architecture

Education:
BS Computer Science
University of Technology (2016-2020)

Skills:
Python, JavaScript, React, FastAPI, PostgreSQL"
```

Length: 2,847 characters

---

### Step 11: Generate Document ID

```python
document_id = str(uuid.uuid4())
# Result: "8f3c4d5e-1a2b-4c3d-9e8f-7a6b5c4d3e2f"
```

---

### Step 12: Store in Memory

```python
pdf_storage[document_id] = text_content
```

**Storage now contains:**
```python
{
    "8f3c4d5e-1a2b-4c3d-9e8f-7a6b5c4d3e2f": "John Doe\nSoftware Engineer\n\nExperience:..."
}
```

---

### Step 13: Create Response

```python
return UploadResponse(
    status="success",
    document_id="8f3c4d5e-1a2b-4c3d-9e8f-7a6b5c4d3e2f",
    text_length=2847,
    message="PDF uploaded successfully. Extracted 2847 characters."
)
```

**Pydantic validates:**
- ✓ `status` is a string
- ✓ `document_id` is a string
- ✓ `text_length` is an integer
- ✓ `message` is a string

---

### Step 14: HTTP Response

**FastAPI sends:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: http://localhost:5173
Content-Length: 167

{
  "status": "success",
  "document_id": "8f3c4d5e-1a2b-4c3d-9e8f-7a6b5c4d3e2f",
  "text_length": 2847,
  "message": "PDF uploaded successfully. Extracted 2847 characters."
}
```

---

### Step 15: Frontend Receives Response

**File:** `frontend/src/components/PdfUpload.tsx`

```typescript
try {
    const response = await uploadPDF(file);
    // response = {
    //     status: "success",
    //     document_id: "8f3c4d5e-...",
    //     text_length: 2847,
    //     message: "PDF uploaded successfully..."
    // }
    
    onUploadSuccess(response.document_id, file.name);
} catch (err) {
    // Error handling
}
```

---

### Step 16: Update UI State

**File:** `frontend/src/App.tsx`

```typescript
const handleUploadSuccess = (docId: string, name: string) => {
    setDocumentId(docId);           // "8f3c4d5e-..."
    setFileName(name);               // "resume.pdf"
    setCurrentQuestion('');
    setCurrentAnswer('');
    setError('');
};
```

**UI now shows:**
- ✓ Document uploaded: `resume.pdf`
- ✓ Question input is enabled
- ✓ User can now ask questions

---

## Example 2: Asking a Question

### User Action
User types "What is this person's job title?" and clicks "Ask Question".

---

### Step 1: Capture Input

**File:** `frontend/src/components/QuestionInput.tsx`

```typescript
const [question, setQuestion] = useState('');

// User types...
// question = "What is this person's job title?"

const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(question.trim());
    setQuestion('');  // Clear input
};
```

---

### Step 2: API Call

**File:** `frontend/src/App.tsx`

```typescript
const handleQuestionSubmit = async (question: string) => {
    setIsAsking(true);
    setCurrentQuestion(question);
    
    const response = await askQuestion(documentId, question);
    // documentId = "8f3c4d5e-1a2b-4c3d-9e8f-7a6b5c4d3e2f"
    // question = "What is this person's job title?"
}
```

**File:** `frontend/src/services/api.ts`

```typescript
export const askQuestion = async (
    documentId: string,
    question: string
): Promise<AnswerResponse> => {
    const payload: QuestionRequest = {
        question,
        document_id: documentId,
    };
    
    const response = await apiClient.post<AnswerResponse>('/api/ask', payload);
    return response.data;
};
```

---

### Step 3: HTTP Request

```http
POST http://localhost:8000/api/ask HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Origin: http://localhost:5173
Content-Length: 96

{
  "question": "What is this person's job title?",
  "document_id": "8f3c4d5e-1a2b-4c3d-9e8f-7a6b5c4d3e2f"
}
```

---

### Step 4: FastAPI Receives & Validates

**File:** `backend/app/api/chat.py`

```python
async def ask_question(request: QuestionRequest):
    # FastAPI + Pydantic automatically:
    # 1. Parse JSON
    # 2. Validate against QuestionRequest schema
    # 3. Create object
    
    # request = QuestionRequest(
    #     question="What is this person's job title?",
    #     document_id="8f3c4d5e-1a2b-4c3d-9e8f-7a6b5c4d3e2f"
    # )
```

**Pydantic validation:**
```python
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)  # ✓ 35 chars
    document_id: str                          # ✓ Valid string
```

---

### Step 5: Check Document Exists

```python
if request.document_id not in pdf_storage:
    raise HTTPException(status_code=404, detail="Document not found")

# pdf_storage = {
#     "8f3c4d5e-1a2b-4c3d-9e8f-7a6b5c4d3e2f": "John Doe\n..."
# }
# ✓ Document found
```

---

### Step 6: Retrieve Context

```python
context = pdf_storage[request.document_id]

# context = "John Doe\nSoftware Engineer\n\nExperience:\nSenior Developer at TechCorp..."
# Length: 2847 characters
```

---

### Step 7: Generate Answer

**File:** `backend/app/services/ollama_service.py`

```python
answer = generate_answer(
    question="What is this person's job title?",
    context="John Doe\nSoftware Engineer\n\nExperience:...",
    model="qwen3.5:2b"
)
```

**Inside the function:**

```python
# 1. Construct prompt
prompt = f"""You are a helpful AI assistant. Answer the question based on the provided document context.

Context:
{context[:8000]}

Question: {question}

Answer:"""

# Actual prompt sent to Ollama:
# "You are a helpful AI assistant. Answer the question based on the provided document context.
#
# Context:
# John Doe
# Software Engineer
#
# Experience:
# Senior Developer at TechCorp (2020-Present)
# ...
#
# Question: What is this person's job title?
#
# Answer:"
```

---

### Step 8: Call Ollama

```python
response = ollama.chat(
    model="qwen3.5:2b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)
```

**HTTP request to Ollama:**
```http
POST http://localhost:11434/api/chat HTTP/1.1
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

---

### Step 9: Ollama Processing

**What Ollama does:**

1. **Check if model is loaded in memory**
   - If not, load from disk (~3 seconds for first request)
   - If yes, skip to step 2

2. **Tokenize the prompt**
   ```
   "You are a helpful" → [1234, 389, 567, ...]
   Length: ~750 tokens
   ```

3. **Run inference**
   - Model processes tokens
   - Generates next token probabilities
   - Samples next token
   - Repeats until done
   - Takes ~2-5 seconds depending on hardware

4. **Return response**

---

### Step 10: Ollama Response

```json
{
  "model": "qwen3.5:2b",
  "created_at": "2026-06-21T10:35:22.123456Z",
  "message": {
    "role": "assistant",
    "content": "Based on the document, this person's job title is Software Engineer. Currently, they work as a Senior Developer at TechCorp."
  },
  "done": true,
  "total_duration": 2847293000,
  "load_duration": 0,
  "prompt_eval_count": 752,
  "eval_count": 28
}
```

---

### Step 11: Extract Answer

```python
answer = response["message"]["content"]
# answer = "Based on the document, this person's job title is Software Engineer. Currently, they work as a Senior Developer at TechCorp."

return answer.strip()
```

---

### Step 12: Create Response

**File:** `backend/app/api/chat.py`

```python
return AnswerResponse(
    answer="Based on the document, this person's job title is Software Engineer. Currently, they work as a Senior Developer at TechCorp.",
    document_id="8f3c4d5e-1a2b-4c3d-9e8f-7a6b5c4d3e2f",
    question="What is this person's job title?"
)
```

---

### Step 13: HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: http://localhost:5173

{
  "answer": "Based on the document, this person's job title is Software Engineer. Currently, they work as a Senior Developer at TechCorp.",
  "document_id": "8f3c4d5e-1a2b-4c3d-9e8f-7a6b5c4d3e2f",
  "question": "What is this person's job title?"
}
```

---

### Step 14: Frontend Receives & Displays

**File:** `frontend/src/App.tsx`

```typescript
try {
    const response = await askQuestion(documentId, question);
    setCurrentAnswer(response.answer);
    // UI updates to show the answer
} catch (err) {
    setError(err.response?.data?.detail || 'Failed to get answer');
} finally {
    setIsAsking(false);
}
```

**UI now shows:**

**Question:**
What is this person's job title?

**Answer:**
Based on the document, this person's job title is Software Engineer. Currently, they work as a Senior Developer at TechCorp.

---

## Timing Breakdown

### Upload Request
- Frontend JS execution: ~1ms
- Network latency: ~1-5ms
- Backend processing:
  - FastAPI routing: ~1ms
  - File reading: ~10-50ms
  - PDF parsing: ~100-500ms
  - Storage: ~1ms
- Total: **~110-560ms**

### Question Request
- Frontend JS execution: ~1ms
- Network latency: ~1-5ms
- Backend processing:
  - FastAPI routing: ~1ms
  - Context retrieval: ~1ms
  - Ollama inference: **~2000-5000ms** (depends on hardware)
- Total: **~2-5 seconds**

---

## Summary

**Upload flow:** File → Validate → Extract text → Store → Return ID

**Question flow:** Question + ID → Retrieve context → LLM → Return answer

**Key insight:** Most time is spent in:
1. PDF text extraction (~100-500ms)
2. LLM inference (~2-5 seconds)

Everything else is fast (<10ms per step).
