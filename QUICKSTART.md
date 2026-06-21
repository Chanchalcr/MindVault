# MindVault Quick Start Guide

Get MindVault up and running in 5 minutes.

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Ollama installed ([ollama.com](https://ollama.com))
- [ ] At least one Ollama model pulled (e.g., `ollama pull qwen3.5:2b`)

## Step 1: Start Ollama (if not already running)

```bash
ollama serve
```

Verify it's working:
```bash
ollama list
```

You should see at least one model listed.

## Step 2: Start Backend

Open a terminal and run:

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

**Backend is ready when you see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Test it: Open [http://localhost:8000/api/health](http://localhost:8000/api/health)

## Step 3: Start Frontend

Open a **new terminal** and run:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend is ready when you see:**
```
  ➜  Local:   http://localhost:5173/
```

## Step 4: Use the App

1. Open [http://localhost:5173](http://localhost:5173) in your browser
2. Upload a PDF document (drag & drop or click to browse)
3. Wait for upload confirmation
4. Type a question about your document
5. Click "Ask Question"
6. See the AI-generated answer

## Troubleshooting

### Backend won't start

**Error: `ModuleNotFoundError: No module named 'fastapi'`**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Error: Port 8000 already in use**
- Another process is using the port
- Kill it: `taskkill /F /IM python.exe` (Windows)
- Or change port: `uvicorn app.main:app --port 8001`

### Frontend won't start

**Error: `npm: command not found`**
- Node.js is not installed or not in PATH
- Install from [nodejs.org](https://nodejs.org)

**Error: Port 5173 already in use**
- Vite will automatically use the next available port (5174, etc.)

### Ollama issues

**Error: "Could not connect to Ollama"**
- Ollama is not running: `ollama serve`
- Check health: `curl http://localhost:11434/api/tags`

**Error: "Model not found"**
- Pull a model: `ollama pull qwen3.5:2b`
- Or use a different model by updating `backend/app/services/ollama_service.py`

**Which model should I use?**
- **Small/Fast**: `qwen3.5:2b` (2.7 GB)
- **Balanced**: `llama3.2` (2 GB)
- **Large/Accurate**: `llama3.3` (8 GB)

### PDF Upload issues

**Error: "Invalid file type"**
- Only PDF files are supported
- Make sure file has .pdf extension

**Error: "File too large"**
- Current limit is 10MB
- Compress your PDF or split it

**Error: "No text could be extracted"**
- PDF might be image-based (scanned)
- Try a text-based PDF

## Next Steps

Once everything works:

1. Try different PDF documents
2. Experiment with different questions
3. Check the API docs at [http://localhost:8000/docs](http://localhost:8000/docs)
4. Read [docs/architecture.md](./docs/architecture.md) to understand the system
5. Check [docs/development-plan.md](./docs/development-plan.md) for future features

## Stopping the App

- **Backend**: Press `Ctrl+C` in the backend terminal
- **Frontend**: Press `Ctrl+C` in the frontend terminal
- **Ollama**: Press `Ctrl+C` if you started it manually (or leave it running)

## Daily Development Workflow

```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate  # Windows (source venv/bin/activate for Linux/Mac)
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3 (optional): Ollama
ollama serve
```

Keep all three running while developing.

## Need Help?

- Check [README.md](./README.md) for more details
- Review [CLAUDE.md](./CLAUDE.md) for development guidelines
- Open an issue on GitHub
