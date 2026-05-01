"""
Translation Service - Handles all translation-related business logic.
Separated from routes for better testability and maintainability.
"""

from typing import Dict, Any, Optional
from services.ai.base_ai_service import BaseAIService
from services.ai.groq_service_refactored import get_groq_service
from config.prompts import PromptManager
from config.settings import Settings
from core.exceptions import TranslationError
from core.decorators import log_execution
from utils.output_cleaner import clean_ai_output


class TranslationService:
    """Service for text translation"""
    
    def __init__(self, ai_service: Optional[BaseAIService] = None):
        """
        Initialize translation service.
        
        Args:
            ai_service: AI service to use (defaults to Groq)
        """
        self.ai_service = ai_service or get_groq_service()
    
    @log_execution
    def translate(
        self,
        text: str,
        target_lang: str,
        source_lang: str = "auto"
    ) -> Dict[str, Any]:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code (default: auto)
        
        Returns:
            Dict with translated_text, source_lang, target_lang
        
        Raises:
            TranslationError: If translation fails
        """
        try:
            # Get prompts from centralized manager
            system = PromptManager.translation_system()
            user = PromptManager.translation_user(text, source_lang, target_lang)
            
            # Call AI service
            translated = self.ai_service.complete(system, user, temperature=0.3)
            
            # Clean output
            translated = clean_ai_output(translated, output_type="text")
            
            return {
                'translated_text': translated,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'source_lang_name': Settings.get_language_name(source_lang),
                'target_lang_name': Settings.get_language_name(target_lang)
            }
            
        except Exception as e:
            raise TranslationError(f"Translation failed: {str(e)}", original_error=e)
    
    @log_execution
    def explain_translation(
        self,
        original: str,
        translation: str
    ) -> Dict[str, str]:
        """
        Explain a translation.
        
        Args:
            original: Original text
            translation: Translated text
        
        Returns:
            Dict with explanation
        
        Raises:
            TranslationError: If explanation fails
        """
        try:
            system = PromptManager.translation_system()
            user = PromptManager.translation_explanation(original, translation)
            
            explanation = self.ai_service.complete(system, user, temperature=0.5)
            explanation = clean_ai_output(explanation, output_type="text")
            
            return {'explanation': explanation}
            
        except Exception as e:
            raise TranslationError(f"Explanation failed: {str(e)}", original_error=e)
    
    @log_execution
    def batch_translate(
        self,
        texts: list[str],
        target_lang: str,
        source_lang: str = "auto"
    ) -> list[Dict[str, Any]]:
        """
        Translate multiple texts.
        
        Args:
            texts: List of texts to translate
            target_lang: Target language code
            source_lang: Source language code (default: auto)
        
        Returns:
            List of translation results
        """
        results = []
        
        for text in texts:
            try:
                result = self.translate(text, target_lang, source_lang)
                results.append(result)
            except TranslationError as e:
                # Continue with other translations
                results.append({
                    'error': str(e),
                    'original_text': text
                })
        
        return results
