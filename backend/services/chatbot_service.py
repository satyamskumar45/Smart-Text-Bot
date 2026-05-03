import json
from typing import Optional

from services.groq_service import translate_text, complete_json
from services.history_service import save_history_entry


def translate(text: str, target: str) -> str:
    if not text or not target:
        raise ValueError("text and target are required")
    return translate_text(text, target)


def summarize(text: str, mode: str = "short", filename: Optional[str] = None) -> dict:
    if not text:
        raise ValueError("No text provided")

    mode = (mode or "short").strip().lower()
    if mode not in {"short", "detailed"}:
        raise ValueError("Mode must be 'short' or 'detailed'")

    system = (
        "You are an expert summarizer. Return a JSON object with three keys: "
        "'paragraph' (a concise 2-3 sentence summary), "
        "'detailed_summary' (a fuller paragraph summary), and "
        "'bullets' (an array of 4-6 key bullet point strings). "
        "Return ONLY the JSON object."
    )
    user = (
        f"Summarize the following text in {mode} mode.\n"
        "Keep the paragraph concise and make detailed_summary more complete.\n\n"
        f"{text}"
    )

    raw = complete_json(system, user, default_structure={"paragraph": "", "detailed_summary": "", "bullets": []})
    try:
        result = json.loads(raw)
    except Exception:
        result = {"paragraph": raw}

    summary_data = {
        "summary": result.get("paragraph", ""),
        "detailed_summary": result.get("detailed_summary") or result.get("paragraph", ""),
        "bullets": result.get("bullets", []),
        "mode": mode,
        "document_name": filename,
    }

    return summary_data


def analyze_sentiment(text: str) -> dict:
    if not text:
        raise ValueError("No text provided")

    system = (
        "You are a sentiment analysis expert. Analyze the sentiment of the provided text. "
        "Return a JSON object with these exact keys: "
        "'sentiment' (one of: positive, negative, neutral), "
        "'positive' (float 0-1), 'negative' (float 0-1), 'neutral' (float 0-1), "
        "'explanation' (one sentence explaining the sentiment). "
        "The three score values must sum to 1.0. Return ONLY the JSON."
    )
    user = f"Analyze the sentiment of this text:\n\n{text}"

    raw = complete_json(system, user)
    try:
        result = json.loads(raw)
    except Exception:
        result = {"sentiment": "neutral", "positive": 0.33, "negative": 0.33, "neutral": 0.34, "explanation": raw}

    sentiment_data = {
        "sentiment": result.get("sentiment", "neutral"),
        "positive": float(result.get("positive", 0.33)),
        "negative": float(result.get("negative", 0.33)),
        "neutral": float(result.get("neutral", 0.34)),
        "explanation": result.get("explanation", ""),
    }

    return sentiment_data


def image_scan(file_bytes: bytes, filename: Optional[str] = None) -> dict:
    # Placeholder: actual OCR/image processing handled elsewhere.
    # Keep a simple, safe response for deployments without heavy dependencies.
    return {"text": "Image processing is currently unavailable for this deployment.", "filename": filename}
