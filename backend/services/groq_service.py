from groq import Groq
import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from config.settings import Settings

# Load environment variables from .env file
# Explicitly set the path to .env in the backend directory
env_path = Path(__file__).parent.parent / ".env"
print(f"[DEBUG] Looking for .env at: {env_path}")
print(f"[DEBUG] .env exists: {env_path.exists()}")

load_dotenv(dotenv_path=env_path)

# Initialize Groq client with API key from environment
api_key = os.getenv("GROQ_API_KEY")

# Debug: Print API key status (without exposing full key)
if api_key:
    print(f"[DEBUG] API key loaded successfully. Length: {len(api_key)}")
    print(f"[DEBUG] API key starts with: {api_key[:10]}...")
    # Strip quotes if present (in case .env has quotes)
    api_key = api_key.strip('"\'')
    print(f"[DEBUG] API key after stripping quotes. Length: {len(api_key)}")
else:
    print("[ERROR] GROQ_API_KEY not found in environment variables!")
    print(f"[DEBUG] Current working directory: {os.getcwd()}")
    print(f"[DEBUG] Environment variables: {list(os.environ.keys())}")
    raise ValueError(
        "GROQ_API_KEY environment variable is not set. "
        f"Please add it to your .env file at: {env_path}"
    )

try:
    client = Groq(api_key=api_key)
    print("[DEBUG] Groq client initialized successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize Groq client: {e}")
    raise


def complete(system: str, user: str, model: str = "llama-3.1-8b-instant", temperature: float = 0.7) -> str:
    """
    Send a message to Groq's chat completion API.
    
    Args:
        system: System prompt
        user: User message
        model: Model to use (default: llama-3.1-8b-instant)
        temperature: Temperature for response randomness (0.0-2.0)
    
    Returns:
        str: The assistant's response
    """
    try:
        print(f"[DEBUG] Calling Groq API with model: {model}")
        print(f"[DEBUG] System prompt: {system[:50]}...")
        print(f"[DEBUG] User message: {user[:50]}...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=temperature,
        )
        
        result = response.choices[0].message.content.strip() # type: ignore
        print(f"[DEBUG] Got response from Groq: {result[:50]}...")
        return result
        
    except Exception as e:
        error_msg = f"Groq API error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)


def complete_json(
    system: str,
    user: str,
    model: str = "llama-3.1-8b-instant",
    default_structure: Optional[dict] = None,
) -> str:
    """
    Send a message to Groq and ensure the response is valid JSON.
    
    Args:
        system: System prompt
        user: User message
        model: Model to use (default: llama-3.1-8b-instant)
        default_structure: Optional fallback structure when JSON parsing fails.
    
    Returns:
        str: JSON string response
    """
    response = complete(system, user, model=model)

    try:
        # Attempt to parse as JSON to ensure validity
        return json.dumps(json.loads(response))
    except json.JSONDecodeError:
        # If response is not JSON, wrap it in the provided default structure if available
        if default_structure is not None:
            fallback = dict(default_structure)
            if "meaning" in fallback and not fallback.get("meaning"):
                fallback["meaning"] = response
            elif "result" in fallback and not fallback.get("result"):
                fallback["result"] = response
            elif "summary" in fallback and not fallback.get("summary"):
                fallback["summary"] = response
            else:
                fallback["raw"] = response
            return json.dumps(fallback)
        return json.dumps({
            "simple": response,
            "professional": response,
            "native": response,
        })


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """
    Translate text using Groq API.
    
    Args:
        text: Text to translate
        target_lang: Target language code or name
        source_lang: Source language code or name (default: auto-detect)
    
    Returns:
        str: Translated text
    """
    print(f"[DEBUG] translate_text called with:")
    print(f"  text: {text[:50]}...")
    print(f"  target_lang: {target_lang}")
    print(f"  source_lang: {source_lang}")
    
    if not text or not text.strip():
        error_msg = "Text to translate cannot be empty"
        print(f"[ERROR] {error_msg}")
        raise ValueError(error_msg)
    
    source_label = "the source language" if source_lang.lower() == "auto" else Settings.get_language_name(source_lang)
    target_label = Settings.get_language_name(target_lang)
    
    system = "You are a professional translator. Provide accurate and natural translations."
    user = (
        f"Translate the following text from {source_label} to {target_label}. "
        f"Only return the translated text without any explanation:\n\n{text}"
    )
    
    try:
        print(f"[DEBUG] Calling complete() function for translation...")
        translated = complete(system, user)
        print(f"[DEBUG] Translation successful: {translated[:50]}...")
        return translated
    except Exception as e:
        error_msg = f"Translation error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)
