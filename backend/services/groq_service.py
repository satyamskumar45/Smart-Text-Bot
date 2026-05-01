import json
import os

from groq import Groq

from config.settings import Settings


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
    response = _get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )

    return response.choices[0].message.content.strip()  # type: ignore[union-attr]


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

    source_label = "the source language" if source_lang.lower() == "auto" else Settings.get_language_name(source_lang)
    target_label = Settings.get_language_name(target_lang)

    system = "You are a professional translator. Provide accurate and natural translations."
    user = (
        f"Translate the following text from {source_label} to {target_label}. "
        f"Only return the translated text without any explanation:\n\n{text}"
    )

    return complete(system, user)
