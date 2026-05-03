from services.groq_service import complete


def correct_text(text: str, mode: str = "correct") -> str:
    if not text:
        raise ValueError("text is required")

    mode = (mode or "correct").strip().lower()
    mode_prompts = {
        "correct": "Correct grammar, spelling, punctuation, and clarity while preserving the original meaning.",
        "formal": "Rewrite this in a polished formal style while preserving the original meaning.",
        "informal": "Rewrite this in a friendly informal style while preserving the original meaning.",
        "simple": "Rewrite this in simple, clear, beginner-friendly language.",
        "professional": "Rewrite this in a concise professional workplace style.",
        "academic": "Rewrite this in an academic style with clear structure.",
        "shorten": "Make this shorter and clearer without losing the core meaning.",
        "expand": "Expand this with helpful detail while keeping it natural.",
    }
    instruction = mode_prompts.get(mode, mode_prompts["correct"])

    try:
        return complete(
            "You are an expert grammar checker and rewriting assistant. Return only the rewritten text.",
            f"{instruction}\n\nText:\n{text}",
            temperature=0.35,
        )
    except Exception:
        pass

    try:
        import language_tool_python
    except Exception as exc:
        if mode == "correct":
            return _basic_cleanup(text)
        raise RuntimeError("Grammar AI service is unavailable in this environment") from exc

    tool = language_tool_python.LanguageTool("en-US")
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    return corrected


def _basic_cleanup(text: str) -> str:
    cleaned = " ".join(text.split())
    if not cleaned:
        return cleaned
    cleaned = cleaned[0].upper() + cleaned[1:]
    if cleaned[-1] not in ".!?":
        cleaned += "."
    replacements = {
        " i ": " I ",
        " im ": " I'm ",
        " dont ": " don't ",
        " cant ": " can't ",
        " wont ": " won't ",
        " ive ": " I've ",
    }
    padded = f" {cleaned} "
    for source, target in replacements.items():
        padded = padded.replace(source, target)
    return padded.strip()
