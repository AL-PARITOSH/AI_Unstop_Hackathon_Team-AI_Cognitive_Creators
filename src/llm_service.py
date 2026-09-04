"""
Groq LLM Service Wrapper with Structured JSON Parsing, Automated Repair, and LangSmith Tracing.
"""

import os
import json
import time
import logging
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
from groq import Groq
from src.config import (
    GROQ_API_KEY, GROQ_LLM_MODEL, GROQ_FALLBACK_LLM_MODEL,
    LANGSMITH_API_KEY, LANGSMITH_PROJECT, is_langsmith_configured
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Configure LangSmith environment variables if configured
if is_langsmith_configured():
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT

FALLBACK_MODELS = [
    GROQ_LLM_MODEL,
    GROQ_FALLBACK_LLM_MODEL,
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "groq/compound-mini",
    "groq/compound",
    "qwen/qwen3.8-27b"
]

def get_groq_client() -> Groq:
    """Initialize Groq client."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing. Please set it in .streamlit/secrets.toml or environment.")
    return Groq(api_key=GROQ_API_KEY)


def generate_structured_output(
    system_prompt: str,
    user_prompt: str,
    response_schema: Type[T],
    model: str = GROQ_LLM_MODEL,
    temperature: float = 0.2,
    max_retries: int = 3
) -> T:
    """
    Call Groq LLM enforcing JSON output, parse into Pydantic schema with repair & model fallback retry logic.
    """
    client = get_groq_client()
    json_schema_desc = json.dumps(response_schema.model_json_schema(), indent=2)

    enhanced_system_prompt = f"{system_prompt}\n\nStrict Output JSON Schema:\n{json_schema_desc}"
    
    messages = [
        {"role": "system", "content": enhanced_system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    last_exception = None
    
    # Filter unique non-empty models
    models_to_try = []
    for m in [model, GROQ_FALLBACK_LLM_MODEL] + FALLBACK_MODELS:
        if m and m not in models_to_try:
            models_to_try.append(m)

    for attempt in range(max_retries + 1):
        attempt_model = models_to_try[attempt % len(models_to_try)]
        raw_text = ""
        
        try:
            logger.info(f"Calling Groq LLM (model: {attempt_model}, attempt: {attempt + 1})")
            response = client.chat.completions.create(
                model=attempt_model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=4096
            )

            raw_text = response.choices[0].message.content.strip()

            # Clean potential backticks if present
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

            # Attempt Pydantic validation
            parsed_data = json.loads(raw_text)
            return response_schema.model_validate(parsed_data)

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Attempt {attempt + 1} with model '{attempt_model}' failed with error: {str(e)}")
            last_exception = e

            # If schema validation failed on non-empty raw_text, try a targeted JSON repair
            if raw_text and attempt == 0:
                logger.info("Attempting targeted JSON repair call...")
                repair_prompt = (
                    f"The previous output failed JSON/schema validation.\n"
                    f"Error: {str(e)}\n"
                    f"Invalid output snippet: {raw_text[:500]}\n"
                    f"Please correct the output to strictly conform to the Pydantic JSON schema."
                )
                messages.append({"role": "assistant", "content": raw_text})
                messages.append({"role": "user", "content": repair_prompt})

            time.sleep(1.0 * (attempt + 1))

    raise RuntimeError(f"Failed to generate valid structured response from Groq after retries. Error: {last_exception}")
