import { useState } from 'react';

interface PdfUploadProps {
  onUploadSuccess: (documentId: string, fileName: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export default function PdfUpload({ onUploadSuccess, isLoading, setIsLoading }: PdfUploadProps) {
  const [error, setError] = useState<string>('');
  const [dragActive, setDragActive] = useState(false);

  const handleFile = async (file: File) => {
    // Validate file type
    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      const { uploadPDF } = await import('../services/api');
      const response = await uploadPDF(file);
      onUploadSuccess(response.document_id, file.name);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to upload PDF';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div className="upload-container">
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          accept=".pdf"
          onChange={handleChange}
          disabled={isLoading}
          style={{ display: 'none' }}
        />
        <label htmlFor="file-upload" className="upload-label">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <p className="upload-text">
            {isLoading ? 'Uploading...' : 'Drop PDF here or click to browse'}
          </p>
          <p className="upload-hint">Maximum file size: 10MB</p>
        </label>
      </div>
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}
