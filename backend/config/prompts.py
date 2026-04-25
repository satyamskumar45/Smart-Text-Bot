"""
Centralized prompt templates for AI services.
All prompts are managed here for easy maintenance and versioning.
"""


class PromptManager:
    """Manages all AI prompt templates"""
    
    # =========================
    # TRANSLATION PROMPTS
    # =========================
    
    @staticmethod
    def translation_system() -> str:
        return "You are a professional translator. Provide accurate and natural translations."
    
    @staticmethod
    def translation_user(text: str, source_lang: str, target_lang: str) -> str:
        source_label = "the source language" if source_lang.lower() == "auto" else source_lang
        return (
            f"Translate the following text from {source_label} to {target_lang}. "
            f"Only return the translated text without any explanation:\n\n{text}"
        )
    
    @staticmethod
    def translation_explanation(original: str, translation: str) -> str:
        return (
            f"Explain this translation in 3-5 lines:\n\n"
            f"Original: {original}\n"
            f"Translation: {translation}"
        )
    
    # =========================
    # GRAMMAR PROMPTS
    # =========================
    
    @staticmethod
    def grammar_fix() -> str:
        return (
            "You are a professional editor. Fix all grammar, spelling, punctuation, and syntax errors. "
            "Return a JSON object with two keys: "
            "'result' (the corrected text) and "
            "'changes' (array of strings describing each correction made). "
            "If no corrections are needed, set changes to an empty array. Return ONLY the JSON."
        )
    
    @staticmethod
    def tone_adjustment(tone_style: str) -> str:
        tone_descriptions = {
            'formal': 'very formal and official',
            'professional': 'professional and business-appropriate',
            'academic': 'academic and scholarly',
            'casual': 'casual and conversational',
            'friendly': 'warm, friendly, and approachable',
        }
        style = tone_descriptions.get(tone_style, tone_descriptions['professional'])
        
        return (
            f"You are an expert writing coach. Rewrite the text to have a {style} tone. "
            "Return a JSON object with two keys: "
            "'result' (the rewritten text) and "
            "'changes' (array of strings noting the tone improvements made). Return ONLY the JSON."
        )
    
    @staticmethod
    def rewrite_text() -> str:
        return (
            "You are a skilled writer. Rewrite the given text to make it clearer, more engaging, "
            "and better structured while preserving the original meaning. "
            "Return a JSON object with two keys: "
            "'result' (the rewritten text) and "
            "'changes' (array of strings describing improvements made). Return ONLY the JSON."
        )
    
    # =========================
    # SUMMARIZATION PROMPTS
    # =========================
    
    @staticmethod
    def summarization() -> str:
        return (
            "You are an expert summarizer. Return a JSON object with two keys: "
            "'paragraph' (a concise 2-3 sentence summary) and "
            "'bullets' (an array of 4-6 key bullet point strings). "
            "Return ONLY the JSON object."
        )
    
    # =========================
    # CHATBOT PROMPTS
    # =========================
    
    @staticmethod
    def chatbot_system() -> str:
        return (
            "You are SmartTextBot, an intelligent AI language assistant. "
            "You help users with translation, text analysis, writing improvement, and language questions. "
            "Be helpful, concise, and friendly."
        )
    
    # =========================
    # SENTIMENT ANALYSIS PROMPTS
    # =========================
    
    @staticmethod
    def sentiment_analysis() -> str:
        return (
            "You are a sentiment analysis expert. Analyze the sentiment of the given text. "
            "Return a JSON object with: "
            "'sentiment' (positive/negative/neutral), "
            "'confidence' (0-100), "
            "'explanation' (brief reason). "
            "Return ONLY the JSON."
        )
    
    # =========================
    # OCR PROMPTS
    # =========================
    
    @staticmethod
    def ocr_structure() -> str:
        return (
            "You are a document formatter. "
            "Convert raw OCR text into clean readable paragraphs. "
            "Remove noise, keep meaning intact. "
            "Do NOT summarize."
        )
    
    @staticmethod
    def ocr_format_user(text: str) -> str:
        return f"Format this text:\n\n{text}"
