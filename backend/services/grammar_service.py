def correct_text(text: str) -> str:
    if not text:
        raise ValueError("text is required")

    try:
        import language_tool_python
    except Exception as exc:
        raise RuntimeError("language_tool_python is not available in this environment") from exc

    tool = language_tool_python.LanguageTool("en-US")
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    return corrected
