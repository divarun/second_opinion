import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from app.prompts import SYSTEM_PROMPT

# --- Environment & LLM Initialization ---
load_dotenv()
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME")

# Allow override via environment variable
SYSTEM_PROMPT = os.getenv("LLM_SYSTEM_PROMPT", SYSTEM_PROMPT)

def call_llm(prompt: str, system_prompt: str = None) -> str:
    """
    Call Ollama local model and return the response text.
    
    Args:
        prompt: The user prompt/question
        system_prompt: Optional system prompt (defaults to SYSTEM_PROMPT)
    """
    # 1. Validation Check
    if not OLLAMA_MODEL_NAME:
        print("ERROR: Missing OLLAMA_MODEL_NAME in environment variables.")
        return "Error: Model name not configured."

    try:
        # 2. Initialize the model
        llm = ChatOllama(
            model=OLLAMA_MODEL_NAME,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0
        )

        # 3. Prepare messages with system prompt
        # Use provided system_prompt or default SYSTEM_PROMPT
        effective_system_prompt = system_prompt if system_prompt is not None else SYSTEM_PROMPT
        messages = [
            ("system", effective_system_prompt),
            ("user", prompt)
        ]

        # 4. Invoke and mimic the .strip() behavior
        response = llm.invoke(messages)
        return response.content.strip()

    except Exception as e:
        # Catch connection errors or missing model errors
        error_msg = f"Could not call Ollama. Ensure it's running and '{OLLAMA_MODEL_NAME}' is pulled. Error: {e}"
        print(f"ERROR: {error_msg}")
        return f"Error: {error_msg}"
