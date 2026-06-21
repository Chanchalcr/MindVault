import ollama
from typing import Optional


class OllamaServiceError(Exception):
    """Custom exception for Ollama service errors"""
    pass


def generate_answer(question: str, context: str, model: str = "qwen3.5:2b") -> str:
    """
    Generate an answer to a question based on provided context using Ollama.

    Args:
        question: The user's question
        context: The document context (PDF text)
        model: Ollama model to use (default: qwen3.5:2b)

    Returns:
        Generated answer as a string

    Raises:
        OllamaServiceError: If Ollama is not available or generation fails
    """
    try:
        # Construct the prompt
        prompt = f"""You are a helpful AI assistant. Answer the question based on the provided document context.

Context:
{context[:8000]}

Question: {question}

Answer:"""

        # Call Ollama to generate response
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract the answer from response
        answer = response["message"]["content"]

        return answer.strip()

    except ollama.ResponseError as e:
        # Ollama returned an error (e.g., model not found)
        raise OllamaServiceError(f"Ollama error: {str(e)}. Make sure the model '{model}' is pulled.")
    except Exception as e:
        # Connection error or other issues
        error_msg = str(e)
        if "Connection" in error_msg or "connect" in error_msg.lower():
            raise OllamaServiceError(
                "Could not connect to Ollama. Make sure Ollama is running (try 'ollama serve' in terminal)."
            )
        raise OllamaServiceError(f"Failed to generate answer: {str(e)}")


def check_ollama_health(model: str = "qwen3.5:2b") -> dict:
    """
    Check if Ollama is running and the model is available.

    Args:
        model: Model name to check

    Returns:
        Dictionary with health status
    """
    try:
        # Try to list models
        models = ollama.list()
        model_names = [m.get("name", m.get("model", "unknown")) for m in models.get("models", [])]

        return {
            "status": "healthy",
            "ollama_running": True,
            "model_available": any(model in name for name in model_names),
            "available_models": model_names
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "ollama_running": False,
            "model_available": False,
            "error": str(e)
        }
