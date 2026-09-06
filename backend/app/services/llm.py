"""
Safar — Centralized LLM Service

Single point of contact for all Gemini API interactions.
Handles initialization, structured output parsing, retries, and errors.
"""

from __future__ import annotations

import json
import re
import logging
from typing import Type, TypeVar

from pydantic import BaseModel
from google import genai
from google.genai import types as genai_types

from app.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------

_client: genai.Client | None = None


def get_client() -> genai.Client:
    """Return a cached Gemini client, creating it on first call."""
    global _client
    if _client is None:
        if not settings.is_api_key_configured:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Please set it in your .env file. "
                "Get a key at https://aistudio.google.com/apikey"
            )
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


# ---------------------------------------------------------------------------
# Helper: extract JSON from LLM text
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> str:
    """
    Extract JSON from LLM response text.
    Handles cases where the model wraps JSON in markdown code fences.
    """
    # Try to find JSON in code fences first
    pattern = r"```(?:json)?\s*\n?([\s\S]*?)\n?```"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()

    # Try to find raw JSON (object or array)
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        if start != -1:
            # Find matching end
            depth = 0
            for i in range(start, len(text)):
                if text[i] == start_char:
                    depth += 1
                elif text[i] == end_char:
                    depth -= 1
                if depth == 0:
                    return text[start : i + 1]

    return text.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_text(prompt: str) -> str:
    """
    Generate plain text from a prompt.

    Returns the raw text response.
    Raises RuntimeError on failure.
    """
    client = get_client()
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )
        if response.text:
            return response.text
        raise RuntimeError("Gemini returned an empty response.")
    except Exception as e:
        logger.error(f"LLM generate_text failed: {e}")
        raise RuntimeError(f"LLM call failed: {e}") from e


def generate_structured(
    prompt: str,
    response_model: Type[T],
    *,
    temperature: float = 0.7,
) -> T:
    """
    Generate structured output and parse it into a Pydantic model.

    Strategy:
    1. Ask the model to return JSON matching the schema.
    2. Extract JSON from the response.
    3. Parse & validate with Pydantic.

    Raises RuntimeError if parsing fails after extraction.
    """
    # Build a schema hint for the prompt
    schema_json = json.dumps(
        response_model.model_json_schema(), indent=2
    )
    full_prompt = (
        f"{prompt}\n\n"
        f"IMPORTANT: Respond ONLY with valid JSON matching this schema:\n"
        f"```json\n{schema_json}\n```\n"
        f"Do not include any text outside the JSON."
    )

    client = get_client()
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=full_prompt,
            config=genai_types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=8192,
                response_mime_type="application/json",
            ),
        )

        raw_text = response.text or ""
        json_str = _extract_json(raw_text)
        data = json.loads(json_str)
        return response_model.model_validate(data)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON: {e}\nRaw: {raw_text[:500]}")
        raise RuntimeError(
            f"LLM returned invalid JSON. Parse error: {e}"
        ) from e
    except Exception as e:
        logger.error(f"LLM generate_structured failed: {e}")
        raise RuntimeError(f"LLM structured call failed: {e}") from e
