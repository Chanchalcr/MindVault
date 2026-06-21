import { useState } from 'react';
import PdfUpload from './components/PdfUpload';
import QuestionInput from './components/QuestionInput';
import AnswerDisplay from './components/AnswerDisplay';
import { askQuestion } from './services/api';
import './App.css';

function App() {
  const [documentId, setDocumentId] = useState<string>('');
  const [fileName, setFileName] = useState<string>('');
  const [currentQuestion, setCurrentQuestion] = useState<string>('');
  const [currentAnswer, setCurrentAnswer] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState<string>('');

  const handleUploadSuccess = (docId: string, name: string) => {
    setDocumentId(docId);
    setFileName(name);
    setCurrentQuestion('');
    setCurrentAnswer('');
    setError('');
  };

  const handleQuestionSubmit = async (question: string) => {
    setError('');
    setIsAsking(true);
    setCurrentQuestion(question);
    setCurrentAnswer('');

    try {
      const response = await askQuestion(documentId, question);
      setCurrentAnswer(response.answer);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to get answer';
      setError(errorMessage);
    } finally {
      setIsAsking(false);
    }
  };

  const handleNewDocument = () => {
    setDocumentId('');
    setFileName('');
    setCurrentQuestion('');
    setCurrentAnswer('');
    setError('');
  };

  return (
    <div className="app">
      <header className="header">
        <h1>MindVault</h1>
        <p className="tagline">AI Knowledge Assistant</p>
      </header>

      <main className="main-content">
        {!documentId ? (
          <div className="upload-section">
            <h2>Upload a PDF Document</h2>
            <p className="instruction">Get started by uploading a PDF to ask questions about</p>
            <PdfUpload
              onUploadSuccess={handleUploadSuccess}
              isLoading={isUploading}
              setIsLoading={setIsUploading}
            />
          </div>
        ) : (
          <div className="chat-section">
            <div className="document-info">
              <span className="document-label">Document:</span>
              <span className="document-name">{fileName}</span>
              <button onClick={handleNewDocument} className="new-doc-button">
                Upload New Document
              </button>
            </div>

            <QuestionInput
              onSubmit={handleQuestionSubmit}
              isLoading={isAsking}
              disabled={!documentId}
            />

            {error && (
              <div className="error-banner">
                <strong>Error:</strong> {error}
              </div>
            )}

            {isAsking && (
              <div className="loading-message">
                <div className="spinner"></div>
                <p>Generating answer...</p>
              </div>
            )}

            {currentAnswer && !isAsking && (
              <AnswerDisplay question={currentQuestion} answer={currentAnswer} />
            )}
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Powered by Ollama • Phase 1 MVP</p>
      </footer>
    </div>
  );
}

export default App;
