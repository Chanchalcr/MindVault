export interface UploadResponse {
  status: string;
  document_id: string;
  text_length: number;
  message: string;
}

export interface QuestionRequest {
  question: string;
  document_id: string;
}

export interface AnswerResponse {
  answer: string;
  document_id: string;
  question: string;
}

export interface ErrorResponse {
  detail: string;
}
