"# MindVault AI

An AI-powered knowledge assistant that lets you upload PDF documents and ask questions about them using local LLM models via Ollama.

## 🚀 Phase 1 MVP - Complete!

**Current Features:**
- ✅ Upload PDF documents
- ✅ Extract text from PDFs
- ✅ Ask questions about uploaded documents
- ✅ Get AI-powered answers using Ollama (local LLM)
- ✅ Clean, modern web interface

## 🛠 Tech Stack

**Frontend:**
- React 19
- TypeScript
- Vite
- Axios

**Backend:**
- Python 3.x
- FastAPI
- pypdf (PDF text extraction)
- Ollama Python client

**AI:**
- Ollama (local LLM runtime)
- Supports models like llama3.2, mistral, qwen, etc.

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** and npm installed
3. **Ollama** installed and running:
   - Download from [ollama.com](https://ollama.com)
   - Pull a model: `ollama pull llama3.2`

## 🏃 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload
```

Backend will run at: `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at: `http://localhost:5173`

### 3. Verify Ollama

Make sure Ollama is running:
```bash
ollama serve
```

And that you have a model pulled:
```bash
ollama pull llama3.2
```

## 📖 Usage

1. Open `http://localhost:5173` in your browser
2. Upload a PDF document (max 10MB)
3. Ask questions about the document
4. Get AI-powered answers instantly

## 🗂 Project Structure

```
MindVault/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── api/             # API endpoints
│   │   ├── services/        # Business logic
│   │   └── models/          # Data models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   └── App.tsx          # Main app
│   └── package.json
├── docs/
│   ├── architecture.md
│   └── development-plan.md
├── CLAUDE.md                # Development guidelines
└── README.md
```

## 🎯 Roadmap

- **Phase 1: MVP** ✅ (Current)
  - Basic PDF upload and Q&A

- **Phase 2: RAG**
  - Document chunking
  - Embeddings
  - Vector database
  - Semantic search

- **Phase 3: Product Features**
  - Multiple documents
  - Document management
  - Chat history
  - User accounts

- **Phase 4: Cloud Deployment**
  - AWS deployment
  - Docker containers
  - Production database

- **Phase 5: Advanced AI**
  - Streaming responses
  - Citations
  - Agents
  - Multimodal support

## 🤝 Development

See [CLAUDE.md](./CLAUDE.md) for development guidelines and architecture decisions.

## 📝 License

MIT" 
