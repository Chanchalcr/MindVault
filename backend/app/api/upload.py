import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from app.models.schemas import UploadResponse
from app.services.pdf_service import extract_text_from_pdf, validate_pdf_size, PDFExtractionError

router = APIRouter(prefix="/api", tags=["upload"])

# Import pdf_storage from main (will be injected)
pdf_storage = {}


def set_pdf_storage(storage: dict):
    """Inject the shared pdf_storage from main"""
    global pdf_storage
    pdf_storage = storage


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and extract its text content.

    Returns a document_id that can be used to ask questions about the document.
    """
    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Expected PDF, got {file.content_type}"
        )

    try:
        # Read file content
        file_content = await file.read()

        # Validate file size (10MB max for MVP)
        validate_pdf_size(len(file_content), max_size_mb=10)

        # Extract text from PDF
        text_content = extract_text_from_pdf(file_content)

        # Generate unique document ID
        document_id = str(uuid.uuid4())

        # Store in memory
        pdf_storage[document_id] = text_content

        return UploadResponse(
            status="success",
            document_id=document_id,
            text_length=len(text_content),
            message=f"PDF uploaded successfully. Extracted {len(text_content)} characters."
        )

    except PDFExtractionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
