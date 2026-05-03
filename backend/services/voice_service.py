import os
import tempfile
import uuid


def create_tts_file(text: str) -> str:
    if not text:
        raise ValueError("text is required")

    try:
        from gtts import gTTS
    except Exception as exc:
        raise RuntimeError("gTTS is not available in this environment") from exc

    tmp_path = os.path.join(tempfile.gettempdir(), f"speech_{uuid.uuid4()}.mp3")
    tts = gTTS(text)
    tts.save(tmp_path)
    return tmp_path
