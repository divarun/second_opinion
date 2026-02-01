"""
LLM Integration
Simplified interface to Ollama for document analysis
"""
import httpx
import json
from typing import Optional, Dict, Any
from config import settings


class LLMClient:
    """Client for interacting with Ollama LLM"""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def generate(
            self,
            prompt: str,
            system_prompt: Optional[str] = None,
            temperature: float = 0.3,
            max_tokens: int = 4000
    ) -> str:
        """
        Generate text completion from prompt

        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            temperature: Randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum response length

        Returns:
            Generated text response
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")

        except httpx.HTTPStatusError as e:
            raise Exception(f"Ollama API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Failed to generate completion: {str(e)}")

    async def generate_json(
            self,
            prompt: str,
            system_prompt: Optional[str] = None,
            temperature: float = 0.3
    ) -> Dict[Any, Any]:
        """
        Generate structured JSON response

        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            temperature: Randomness level

        Returns:
            Parsed JSON dictionary
        """
        # Enhance system prompt for JSON output
        json_system = (system_prompt or "") + "\n\nYou must respond with valid JSON only. No markdown, no explanation."

        response = await self.generate(
            prompt=prompt,
            system_prompt=json_system,
            temperature=temperature
        )

        # Clean response (remove markdown code blocks if present)
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}\nResponse: {response}")

    async def check_health(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global LLM client instance
llm_client = LLMClient()