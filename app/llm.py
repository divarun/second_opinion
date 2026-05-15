"""
LLM Integration
Multi-provider LLM client supporting Ollama and Anthropic
"""
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import httpx

from app.config import settings


class BaseLLMClient(ABC):
    """Common interface for all LLM providers"""

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Dict[Any, Any]:
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        pass

    @abstractmethod
    async def close(self):
        pass

    @staticmethod
    def _extract_json(response: str) -> Dict:
        """Strip markdown fences and parse JSON."""
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


class OllamaClient(BaseLLMClient):
    """Client for Ollama local LLM service"""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.client = httpx.AsyncClient(timeout=settings.ollama_timeout)

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Dict[Any, Any]:
        json_system = (system_prompt or "") + "\n\nYou must respond with valid JSON only. No markdown, no explanation."

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": 4000},
        }
        if json_system:
            payload["system"] = json_system

        try:
            response = await self.client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            raw = response.json().get("response", "")
            return self._extract_json(raw)
        except httpx.HTTPStatusError as e:
            raise Exception(f"Ollama API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")

    async def check_health(self) -> bool:
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()


class AnthropicLLMClient(BaseLLMClient):
    """Client for Anthropic Claude API"""

    def __init__(self):
        try:
            import anthropic
        except ImportError:
            raise RuntimeError("anthropic package is required for the Anthropic provider. Run: pip install anthropic")

        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Dict[Any, Any]:
        json_system = (system_prompt or "") + "\n\nYou must respond with valid JSON only. No markdown, no explanation."

        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=temperature,
                system=json_system,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text
            return self._extract_json(raw)
        except Exception as e:
            raise Exception(f"Anthropic generation failed: {str(e)}")

    async def check_health(self) -> bool:
        return bool(settings.anthropic_api_key)

    async def close(self):
        await self.client.close()


def get_llm_client() -> BaseLLMClient:
    if settings.llm_provider == "anthropic":
        return AnthropicLLMClient()
    return OllamaClient()


llm_client = get_llm_client()
