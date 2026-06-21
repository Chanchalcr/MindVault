import axios from 'axios';
import type { UploadResponse, QuestionRequest, AnswerResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export const checkHealth = async () => {
  const response = await apiClient.get('/api/health');
  return response.data;
};
