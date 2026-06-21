from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response after PDF upload"""
    status: str
    document_id: str
    text_length: int
    message: str


class QuestionRequest(BaseModel):
    """Request to ask a question about a document"""
    question: str = Field(..., min_length=1, description="The question to ask")
    document_id: str = Field(..., description="ID of the uploaded document")


class AnswerResponse(BaseModel):
    """Response containing the AI-generated answer"""
    answer: str
    document_id: str
    question: str
