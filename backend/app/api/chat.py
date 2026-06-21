from fastapi import APIRouter, HTTPException, status

from app.models.schemas import QuestionRequest, AnswerResponse
from app.services.ollama_service import generate_answer, OllamaServiceError

router = APIRouter(prefix="/api", tags=["chat"])

# Import pdf_storage from main (will be injected)
pdf_storage = {}


def set_pdf_storage(storage: dict):
    """Inject the shared pdf_storage from main"""
    global pdf_storage
    pdf_storage = storage


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about an uploaded document.

    Requires a valid document_id from a previously uploaded PDF.
    """
    # Check if document exists
    if request.document_id not in pdf_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found. Please upload a PDF first."
        )

    # Get the document context
    context = pdf_storage[request.document_id]

    try:
        # Generate answer using Ollama
        answer = generate_answer(
            question=request.question,
            context=context
        )

        return AnswerResponse(
            answer=answer,
            document_id=request.document_id,
            question=request.question
        )

    except OllamaServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {str(e)}"
        )
