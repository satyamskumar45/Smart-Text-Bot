import json
import os
import logging

from groq import Groq

from config.settings import Settings


logger = logging.getLogger(__name__)
_client = None


def _get_client():
    global _client

    if _client is not None:
        return _client

    api_key = (os.getenv("GROQ_API_KEY") or "").strip().strip("\"'")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is not set.")

    _client = Groq(api_key=api_key)
    return _client


def complete(system: str, user: str, model: str = "llama-3.1-8b-instant", temperature: float = 0.7) -> str:
    try:
        response = _get_client().chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content.strip()  # type: ignore[union-attr]
    except Exception as e:
        logger.exception("Groq API call failed")
        raise RuntimeError("GROQ API error") from e


def complete_json(system: str, user: str, model: str = "llama-3.1-8b-instant", default_structure=None) -> str:
    response = complete(system, user, model=model, temperature=0.3)

    try:
        return json.dumps(json.loads(response))
    except json.JSONDecodeError:
        if default_structure is not None:
            fallback = dict(default_structure)
            if "paragraph" in fallback and not fallback.get("paragraph"):
                fallback["paragraph"] = response
            elif "summary" in fallback and not fallback.get("summary"):
                fallback["summary"] = response
            else:
                fallback["raw"] = response
            return json.dumps(fallback)

        return json.dumps({"result": response})


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    if not text or not text.strip():
        raise ValueError("Text to translate cannot be empty")

    if not target_lang or not isinstance(target_lang, str):
        raise ValueError("target_lang is required")

    # Resolve language labels safely
    try:
        source_label = "the source language" if source_lang.lower() == "auto" else Settings.get_language_name(source_lang)
    except Exception:
        source_label = "the source language"

    try:
        target_label = Settings.get_language_name(target_lang)
        if not target_label:
            raise ValueError(f"Unknown target language: {target_lang}")
    except ValueError:
        raise
    except Exception:
        raise ValueError(f"Unknown target language: {target_lang}")

    system = "You are a professional translator. Provide accurate and natural translations."
    user = (
        f"Translate the following text from {source_label} to {target_label}. "
        f"Only return the translated text without any explanation:\n\n{text}"
    )

    try:
        return complete(system, user)
    except RuntimeError:
        # Propagate Groq-related runtime errors for the route to catch and handle
        raise
    except Exception as e:
        logger.exception("Unexpected error during translation")
        raise RuntimeError("Translation failed") from e
