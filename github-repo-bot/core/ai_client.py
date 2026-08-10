#!/usr/bin/env python3
"""OpenAI client wrapper for structured project analysis."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


class AIClient:
    """Thin wrapper around the OpenAI chat API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = None

        if self.api_key and OpenAI is not None:
            self._client = OpenAI(api_key=self.api_key)

    @property
    def available(self) -> bool:
        return self._client is not None

    def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.4,
    ) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError(
                "OpenAI is not configured. Set OPENAI_API_KEY and install openai: pip install openai"
            )

        response = self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content or "{}"
        return self._parse_json(content)

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise
