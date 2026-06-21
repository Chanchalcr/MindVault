# MindVault Frontend

React + TypeScript + Vite frontend for MindVault AI Knowledge Assistant.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Make sure the backend is running at `http://localhost:8000`

## Run

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Features

- Upload PDF documents (max 10MB)
- Ask questions about uploaded documents
- Get AI-powered answers using Ollama
- Clean, modern UI with drag-and-drop support

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── PdfUpload.tsx    # PDF upload with drag-and-drop
│   │   ├── QuestionInput.tsx # Question input form
│   │   └── AnswerDisplay.tsx # Answer display
│   ├── services/            # API communication
│   │   └── api.ts           # Backend API client
│   ├── types/               # TypeScript types
│   │   └── index.ts         # Type definitions
│   ├── App.tsx              # Main application
│   ├── App.css              # Styling
│   └── main.tsx             # Entry point
├── .env                     # Environment variables
└── package.json
```
