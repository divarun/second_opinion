"""LLM integration with Ollama, including async support, retry logic, and timeouts."""
import asyncio
from typing import Optional
from langchain_ollama import ChatOllama
from app.config import settings
from app.logger import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import SYSTEM_PROMPT after config to avoid circular imports
from app.prompts import SYSTEM_PROMPT


class LLMError(Exception):
    """Exception raised for LLM-related errors."""
    pass


@retry(
    stop=stop_after_attempt(settings.llm_max_retries),
    wait=wait_exponential(multiplier=1, min=settings.llm_retry_delay_min, max=settings.llm_retry_delay_max),
    retry=retry_if_exception_type((ConnectionError, TimeoutError, LLMError)),
    reraise=True
)
def call_llm(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Call Ollama local model and return the response text (synchronous version).
    
    Args:
        prompt: The user prompt/question
        system_prompt: Optional system prompt (defaults to SYSTEM_PROMPT from config)
        
    Returns:
        Response text from the LLM
        
    Raises:
        LLMError: If model is not configured or call fails
    """
    # Validation check
    if not settings.ollama_model_name:
        error_msg = "Missing OLLAMA_MODEL_NAME in environment variables"
        logger.error(error_msg)
        raise LLMError(error_msg)

    try:
        # Initialize the model
        llm = ChatOllama(
            model=settings.ollama_model_name,
            base_url=settings.ollama_base_url,
            temperature=settings.llm_temperature,
            timeout=settings.ollama_timeout
        )

        # Prepare messages with system prompt
        effective_system_prompt = system_prompt if system_prompt is not None else (
            settings.llm_system_prompt or SYSTEM_PROMPT
        )
        messages = [
            ("system", effective_system_prompt),
            ("user", prompt)
        ]

        # Invoke and return response
        logger.debug(f"Calling LLM with model {settings.ollama_model_name}")
        response = llm.invoke(messages)
        result = response.content.strip()
        logger.debug(f"LLM response received, length: {len(result)}")
        return result

    except Exception as e:
        error_msg = f"Could not call Ollama. Ensure it's running and '{settings.ollama_model_name}' is pulled. Error: {e}"
        logger.error(error_msg, exc_info=True)
        raise LLMError(error_msg) from e


async def call_llm_async(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Call Ollama local model asynchronously and return the response text.
    
    This function runs the synchronous call_llm in a thread pool to avoid
    blocking the event loop, since langchain_ollama doesn't provide async support.
    
    Args:
        prompt: The user prompt/question
        system_prompt: Optional system prompt (defaults to SYSTEM_PROMPT from config)
        
    Returns:
        Response text from the LLM
        
    Raises:
        LLMError: If model is not configured or call fails
    """
    # Run the synchronous call_llm in a thread pool to avoid blocking
    logger.debug(f"Calling LLM async (via thread pool) with model {settings.ollama_model_name}")
    try:
        result = await asyncio.to_thread(call_llm, prompt, system_prompt)
        logger.debug(f"LLM async response received, length: {len(result)}")
        return result
    except LLMError:
        # Re-raise LLMError as-is
        raise
    except Exception as e:
        error_msg = f"Could not call Ollama. Ensure it's running and '{settings.ollama_model_name}' is pulled. Error: {e}"
        logger.error(error_msg, exc_info=True)
        raise LLMError(error_msg) from e
