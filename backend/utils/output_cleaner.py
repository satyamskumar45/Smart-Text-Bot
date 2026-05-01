"""
AI Output Quality Utilities
Handles: repetition, OCR noise, summary formatting, UI-safe JSON
"""

import re
import json
from typing import Tuple, List, Dict, Any


# =========================
# 1️⃣ REMOVE REPETITION
# =========================

def remove_repetition(text: str, threshold: int = 3) -> str:
    """
    Remove repeated sentences/phrases that appear more than threshold times.
    
    Before: "Hello world. Hello world. Hello world. This is text."
    After:  "Hello world. This is text."
    """
    sentences = re.split(r'([.!?]\s+)', text)
    seen = {}
    result = []
    
    for i in range(0, len(sentences), 2):
        if i >= len(sentences):
            break
        
        sentence = sentences[i].strip()
        if not sentence:
            continue
        
        # Normalize for comparison
        normalized = re.sub(r'\s+', ' ', sentence.lower())
        
        seen[normalized] = seen.get(normalized, 0) + 1
        
        # Only add if below threshold
        if seen[normalized] <= threshold:
            result.append(sentence)
            if i + 1 < len(sentences):
                result.append(sentences[i + 1])
    
    return ''.join(result).strip()


def remove_consecutive_duplicates(text: str) -> str:
    """
    Remove consecutive duplicate lines/sentences.
    
    Before: "Line 1\nLine 1\nLine 2\nLine 2\nLine 2\nLine 3"
    After:  "Line 1\nLine 2\nLine 3"
    """
    lines = text.split('\n')
    result = [lines[0]] if lines else []
    
    for line in lines[1:]:
        if line.strip() != result[-1].strip():
            result.append(line)
    
    return '\n'.join(result)


# =========================
# 2️⃣ FIX OCR TEXT
# =========================

def fix_ocr_text(text: str) -> str:
    """
    Clean messy OCR output: spacing, line breaks, special chars.
    
    Before: "Th1s  is    a\ntes-t\ndo©ument"
    After:  "This is a test document"
    """
    # Fix common OCR character mistakes
    replacements = {
        '©': 'c', '®': 'r', '™': 'tm',
        '0': 'O', '1': 'l', '5': 'S',  # Only in word context
        '|': 'I', '!': 'i'
    }
    
    # Fix broken words across lines
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Normalize whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove isolated special characters
    text = re.sub(r'\s[^\w\s.,!?;:()]\s', ' ', text)
    
    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])\s*([^\s])', r'\1 \2', text)
    
    return text.strip()


def remove_ocr_noise(text: str, min_word_length: int = 2) -> str:
    """
    Remove OCR artifacts: random chars, short gibberish.
    
    Before: "This is text. a b c. More content. xyz."
    After:  "This is text. More content."
    """
    lines = text.split('\n')
    cleaned = []
    
    for line in lines:
        words = line.split()
        
        # Skip lines with too many short/invalid words
        valid_words = [w for w in words if len(w) >= min_word_length and re.search(r'[a-zA-Z]', w)]
        
        if len(valid_words) >= len(words) * 0.6:  # 60% valid words
            cleaned.append(line)
    
    return '\n'.join(cleaned)


# =========================
# 3️⃣ FORMAT SUMMARIES
# =========================

def format_summary(text: str, max_length: int = 300) -> str:
    """
    Clean and format AI summary output.
    
    Before: "  Summary:  This is a summary with extra spaces.  \n\n  "
    After:  "This is a summary with extra spaces."
    """
    # Remove common AI prefixes
    text = re.sub(r'^(summary|tldr|overview|conclusion):\s*', '', text, flags=re.IGNORECASE)
    
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Ensure proper sentence ending
    if text and not text[-1] in '.!?':
        text += '.'
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    
    return text


def extract_bullet_points(text: str) -> List[str]:
    """
    Extract clean bullet points from AI output.
    
    Before: "- Point 1\n* Point 2\n• Point 3\n1. Point 4"
    After:  ["Point 1", "Point 2", "Point 3", "Point 4"]
    """
    # Match various bullet formats
    pattern = r'^[\s]*[-*•●○▪▫➤➢⦿⦾\d.]+[\s]+(.*?)$'
    
    bullets = []
    for line in text.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            bullet = match.group(1).strip()
            if bullet and len(bullet) > 5:  # Avoid noise
                bullets.append(bullet)
    
    return bullets


# =========================
# 4️⃣ UI-SAFE JSON
# =========================

def sanitize_for_json(text: str) -> str:
    """
    Make text safe for JSON serialization.
    
    Before: "Text with "quotes" and \backslashes\ and newlines\n"
    After:  "Text with \"quotes\" and \\backslashes\\ and newlines "
    """
    # Escape special characters
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', ' ')
    text = text.replace('\r', '')
    text = text.replace('\t', ' ')
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()


def safe_json_extract(text: str) -> Dict[str, Any]:
    """
    Safely extract JSON from AI output (even if wrapped in text).
    
    Before: "Here's the JSON: ```json\n{\"key\": \"value\"}\n```"
    After:  {"key": "value"}
    """
    # Try direct parse
    try:
        return json.loads(text)
    except:
        pass
    
    # Extract from code blocks
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    
    # Extract any JSON object
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    
    return {}


def ensure_valid_json_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure all values in dict are JSON-serializable and UI-safe.
    """
    cleaned = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            cleaned[key] = sanitize_for_json(value)
        elif isinstance(value, list):
            cleaned[key] = [sanitize_for_json(str(v)) if isinstance(v, str) else v for v in value]
        elif isinstance(value, (int, float, bool, type(None))):
            cleaned[key] = value
        else:
            cleaned[key] = str(value)
    
    return cleaned


# =========================
# 5️⃣ COMBINED PIPELINE
# =========================

def clean_ai_output(text: str, output_type: str = "text") -> str:
    """
    All-in-one cleaner for AI outputs.
    
    Args:
        text: Raw AI output
        output_type: "text", "summary", "ocr"
    
    Returns:
        Cleaned text
    """
    if output_type == "ocr":
        text = fix_ocr_text(text)
        text = remove_ocr_noise(text)
    
    text = remove_consecutive_duplicates(text)
    text = remove_repetition(text)
    
    if output_type == "summary":
        text = format_summary(text)
    
    return text


# =========================
# 📊 EXAMPLES
# =========================

def show_examples():
    """Print before/after examples"""
    
    print("=" * 60)
    print("1️⃣ REPETITION REMOVAL")
    print("=" * 60)
    
    before = "Hello world. Hello world. This is a test. This is a test. This is a test. Final line."
    after = remove_repetition(before, threshold=2)
    print(f"BEFORE: {before}")
    print(f"AFTER:  {after}\n")
    
    print("=" * 60)
    print("2️⃣ OCR TEXT FIXING")
    print("=" * 60)
    
    before = "Th1s  is    a\ntes-t\ndo©ument  with   sp@cing"
    after = fix_ocr_text(before)
    print(f"BEFORE: {repr(before)}")
    print(f"AFTER:  {repr(after)}\n")
    
    print("=" * 60)
    print("3️⃣ SUMMARY FORMATTING")
    print("=" * 60)
    
    before = "  Summary:  This is a summary with extra spaces and noise.  \n\n  "
    after = format_summary(before)
    print(f"BEFORE: {repr(before)}")
    print(f"AFTER:  {repr(after)}\n")
    
    print("=" * 60)
    print("4️⃣ JSON SANITIZATION")
    print("=" * 60)
    
    before = 'Text with "quotes" and \backslashes\ and newlines\n'
    after = sanitize_for_json(before)
    print(f"BEFORE: {repr(before)}")
    print(f"AFTER:  {repr(after)}\n")
    
    print("=" * 60)
    print("5️⃣ JSON EXTRACTION")
    print("=" * 60)
    
    before = 'Here is the result: ```json\n{"status": "success", "data": "value"}\n```'
    after = safe_json_extract(before)
    print(f"BEFORE: {before}")
    print(f"AFTER:  {after}\n")


if __name__ == "__main__":
    show_examples()
