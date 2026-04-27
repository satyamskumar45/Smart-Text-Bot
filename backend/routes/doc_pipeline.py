from flask import Blueprint, request

from core.exceptions import OCRError
from services.document.ocr_service import OCRService
from services.groq_service import complete
from utils.output_cleaner import (
    clean_ai_output,
    safe_json_extract,
    ensure_valid_json_response,
    remove_repetition,
    format_summary,
    extract_bullet_points,
)
from utils.response import success, error
import re


doc_pipeline_bp = Blueprint('doc_pipeline', __name__)
ocr_service = OCRService()


def clean_text(text: str) -> str:
    return clean_ai_output(text, output_type="ocr")


def remove_noise(text: str) -> str:
    noise_keywords = [
        "File Name",
        "Pages",
        "Words",
        "Language",
        "Date",
        "DOCUMENT INFO",
    ]

    lines = re.split(r"[.\n]", text)
    cleaned = []

    for line in lines:
        line = line.strip()
        if any(keyword.lower() in line.lower() for keyword in noise_keywords):
            continue
        if len(line) > 25:
            cleaned.append(line)

    return ". ".join(cleaned)


def structure_text(text: str) -> str:
    sentences = re.split(r"(?<=[.!?]) +", text)

    paragraphs = []
    current = []

    for sentence in sentences:
        if len(sentence.strip()) < 20:
            continue

        current.append(sentence.strip())
        if len(current) >= 4:
            paragraphs.append(" ".join(current))
            current = []

    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs)


def ai_structure(text: str) -> str:
    try:
        system = (
            "You are a document formatter.\n"
            "Convert raw OCR text into clean readable paragraphs.\n"
            "Remove noise, keep meaning intact.\n"
            "Do NOT summarize.\n"
        )
        user = f"Format this text:\n\n{text}"
        return complete(system, user, temperature=0.2)
    except Exception as exc:
        print(f"[PIPELINE] AI structuring fallback used: {exc}")
        return structure_text(text)


def translate_text(text: str, target_lang: str) -> str:
    if target_lang.lower() in ["en", "english"]:
        return text

    system = "Translate the text accurately. Return ONLY translated text."
    user = f"Translate into {target_lang}:\n\n{text}"
    return complete(system, user, temperature=0.3)


def safe_json_parse(text: str):
    return safe_json_extract(text)


def summarize_text(text: str):
    system = (
        "You are an expert summarizer.\n"
        'Return ONLY JSON:\n{ "paragraph": "2-3 line summary", "bullets": ["point1","point2"] }'
    )
    user = f"Summarize this:\n\n{text}"

    response = complete(system, user, temperature=0.4)
    response = remove_repetition(response)
    data = safe_json_parse(response)

    if data:
        summary = format_summary(data.get("paragraph", ""))
        bullets = data.get("bullets", [])
        if not bullets:
            bullets = extract_bullet_points(response)
        return summary, bullets

    return format_summary(response), []


@doc_pipeline_bp.route("/pipeline", methods=["POST"])
def pipeline():
    try:
        file = request.files.get("file")
        target_lang = request.form.get("target_lang", "en")

        if not file:
            return error("No file uploaded", 400)

        print("\n[PIPELINE] Started")

        try:
            image_bytes = file.read()
            raw_text = ocr_service.extract_text_simple(image_bytes, preprocess=True)
            if not raw_text.strip():
                raise OCRError("No text detected in image")
            print(f"[PIPELINE] OCR complete: {len(raw_text)} chars")
        except OCRError as exc:
            print(f"[PIPELINE] OCR unavailable or failed: {exc}")
            message = str(exc)
            status_code = 503 if "currently unavailable" in message else 500
            return error(message, status_code)
        except Exception as exc:
            return error(f"OCR failed: {str(exc)}", 500)

        cleaned = clean_text(raw_text)
        noise_free = remove_noise(cleaned)
        print("[PIPELINE] Text cleaned")

        structured = ai_structure(noise_free)
        print("[PIPELINE] Text structured")

        try:
            translated = translate_text(structured, target_lang)
            print("[PIPELINE] Translation complete")
        except Exception as exc:
            translated = structured
            print(f"[PIPELINE] Translation failed, continuing with source text: {exc}")

        try:
            summary, bullets = summarize_text(translated)
            print("[PIPELINE] Summary complete")
        except Exception as exc:
            summary = "Summary failed"
            bullets = []
            print(f"[PIPELINE] Summary failed: {exc}")

        result = ensure_valid_json_response(
            {
                "extracted_text": structured,
                "translation": translated,
                "summary": summary,
                "bullets": bullets,
            }
        )

        print("[PIPELINE] Completed")
        return success(result)

    except Exception as exc:
        print(f"[PIPELINE] Unexpected error: {exc}")
        return error(f"Pipeline failed: {str(exc)}", 500)
