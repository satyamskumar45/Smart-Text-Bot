from flask import Blueprint, request
from utils.response import success, error
from services.groq_service import complete
from utils.output_cleaner import (
    clean_ai_output,
    safe_json_extract,
    ensure_valid_json_response,
    remove_repetition,
    format_summary,
    extract_bullet_points
)

from PIL import Image
import pytesseract
import io
import json
import re

doc_pipeline_bp = Blueprint('doc_pipeline', __name__)

# ✅ Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =========================
# 🧹 STEP 1 — LIGHT CLEANING (DON'T OVERDO)
# =========================
def clean_text(text: str) -> str:
    text = clean_ai_output(text, output_type="ocr")
    return text


# =========================
# 🚫 STEP 2 — REMOVE ONLY TRUE METADATA
# =========================
def remove_noise(text: str) -> str:
    noise_keywords = [
        "File Name", "Pages", "Words",
        "Language", "Date", "DOCUMENT INFO"
    ]

    lines = re.split(r'[.\n]', text)
    cleaned = []

    for line in lines:
        line = line.strip()

        if any(k.lower() in line.lower() for k in noise_keywords):
            continue

        if len(line) > 25:
            cleaned.append(line)

    return ". ".join(cleaned)


# =========================
# 🧠 STEP 3 — STRUCTURE TEXT (FALLBACK)
# =========================
def structure_text(text: str) -> str:
    sentences = re.split(r'(?<=[.!?]) +', text)

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


# =========================
# 🤖 STEP 4 — AI STRUCTURING (PRIMARY)
# =========================
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
        return structure_text(text)  # fallback


# =========================
# 🌍 STEP 5 — TRANSLATION
# =========================
def translate_text(text: str, target_lang: str) -> str:
    if target_lang.lower() in ["en", "english"]:
        return text

    system = "Translate the text accurately. Return ONLY translated text."
    user = f"Translate into {target_lang}:\n\n{text}"

    return complete(system, user, temperature=0.3)


# =========================
# 📄 STEP 6 — SAFE JSON PARSER
# =========================
def safe_json_parse(text: str):
    return safe_json_extract(text)


# =========================
# 📄 STEP 7 — SUMMARIZATION
# =========================
def summarize_text(text: str):
    system = (
        "You are an expert summarizer.\n"
        "Return ONLY JSON:\n"
        "{ \"paragraph\": \"2-3 line summary\", \"bullets\": [\"point1\",\"point2\"] }"
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

    # fallback
    return format_summary(response), []


# =========================
# 🚀 MAIN PIPELINE
# =========================
@doc_pipeline_bp.route('/pipeline', methods=['POST'])
def pipeline():
    try:
        file = request.files.get('file')
        target_lang = request.form.get('target_lang', 'en')

        if not file:
            return error("No file uploaded", 400)

        print("\n🚀 PIPELINE STARTED")

        # =========================
        # STEP 1 — OCR
        # =========================
        try:
            image = Image.open(io.BytesIO(file.read()))
            raw_text = pytesseract.image_to_string(image)

            if not raw_text.strip():
                raise Exception("No text detected")

            print(f"✅ OCR DONE: {len(raw_text)} chars")

        except Exception as e:
            return error(f"OCR failed: {str(e)}", 500)

        # =========================
        # STEP 2 — CLEANING
        # =========================
        cleaned = clean_text(raw_text)
        noise_free = remove_noise(cleaned)

        print("✅ TEXT CLEANED")

        # =========================
        # STEP 3 — STRUCTURE
        # =========================
        structured = ai_structure(noise_free)

        print("✅ TEXT STRUCTURED")

        # =========================
        # STEP 4 — TRANSLATE
        # =========================
        try:
            translated = translate_text(structured, target_lang)
            print("✅ TRANSLATION DONE")
        except Exception as exc:
            translated = structured
            print(f"⚠️ TRANSLATION FAILED: {exc}")

        # =========================
        # STEP 5 — SUMMARY
        # =========================
        try:
            summary, bullets = summarize_text(translated)
            print("✅ SUMMARY DONE")
        except Exception as exc:
            summary = "Summary failed"
            bullets = []
            print(f"⚠️ SUMMARY FAILED: {exc}")

        print("🎉 PIPELINE COMPLETED\n")

        # Ensure UI-safe output
        result = ensure_valid_json_response({
            "extracted_text": structured,
            "translation": translated,
            "summary": summary,
            "bullets": bullets
        })

        return success(result)

    except Exception as e:
        print(f"❌ PIPELINE ERROR: {str(e)}")
        return error(f"Pipeline failed: {str(e)}", 500)
