"""
Base generator class with AI integration.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Optional


class AIProvider:
    """Wrapper for AI API calls supporting multiple providers."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = "anthropic",
        model: Optional[str] = None
    ):
        """
        Initialize AI provider.

        Args:
            api_key: API key (or use environment variable)
            provider: 'anthropic' or 'openai'
            model: Model name (defaults based on provider)
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_default_model()
        self._client = None

    def _get_api_key(self) -> str:
        """Get API key from environment."""
        if self.provider == "anthropic":
            key = os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise ValueError(
                    "ANTHROPIC_API_KEY environment variable not set. "
                    "Set it or pass api_key parameter."
                )
            return key
        elif self.provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable not set. "
                    "Set it or pass api_key parameter."
                )
            return key
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _get_default_model(self) -> str:
        """Get default model for provider."""
        if self.provider == "anthropic":
            return "claude-sonnet-4-20250514"
        elif self.provider == "openai":
            return "gpt-4o"
        return "claude-sonnet-4-20250514"

    @property
    def client(self):
        """Lazy-load the API client."""
        if self._client is None:
            if self.provider == "anthropic":
                try:
                    from anthropic import Anthropic
                    self._client = Anthropic(api_key=self.api_key)
                except ImportError:
                    raise ImportError(
                        "anthropic package required. Install with: pip install anthropic"
                    )
            elif self.provider == "openai":
                try:
                    from openai import OpenAI
                    self._client = OpenAI(api_key=self.api_key)
                except ImportError:
                    raise ImportError(
                        "openai package required. Install with: pip install openai"
                    )
        return self._client

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using the AI model.

        Args:
            prompt: User prompt
            system: System prompt (optional)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Generated text response
        """
        if self.provider == "anthropic":
            return self._generate_anthropic(prompt, system, max_tokens, temperature)
        elif self.provider == "openai":
            return self._generate_openai(prompt, system, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _generate_anthropic(
        self,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Anthropic API."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def _generate_openai(
        self,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using OpenAI API."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

    def generate_json(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096
    ) -> dict:
        """
        Generate and parse JSON response.

        Args:
            prompt: User prompt (should request JSON output)
            system: System prompt
            max_tokens: Maximum tokens

        Returns:
            Parsed JSON as dictionary
        """
        # Add JSON instruction to system prompt
        json_system = (system or "") + "\n\nRespond only with valid JSON. No other text."

        response = self.generate(prompt, json_system, max_tokens, temperature=0.3)

        # Clean response and parse JSON
        response = response.strip()

        # Handle markdown code blocks
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        return json.loads(response.strip())


class BaseGenerator(ABC):
    """Abstract base class for content generators."""

    def __init__(self, ai_provider: AIProvider):
        """
        Initialize generator with AI provider.

        Args:
            ai_provider: Configured AIProvider instance
        """
        self.ai = ai_provider

    @abstractmethod
    def generate(self, content: str, **kwargs):
        """Generate output from content."""
        pass
