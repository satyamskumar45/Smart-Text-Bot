"""
Groq AI Service - Implementation of BaseAIService for Groq API.
Includes retry logic, error handling, and fallback mechanisms.
"""

from groq import Groq
import json
from typing import Dict, Any, Optional

from services.ai.base_ai_service import BaseAIService
from core.exceptions import AIServiceError
from core.decorators import retry_with_fallback, log_execution
from config.settings import Settings
from utils.output_cleaner import safe_json_extract


class GroqService(BaseAIService):
    """Groq AI service implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq service.
        
        Args:
            api_key: Groq API key (defaults to Settings.GROQ_API_KEY)
        """
        self.api_key = api_key or Settings.GROQ_API_KEY
        
        if not self.api_key:
            raise AIServiceError("Groq API key not configured")
        
        try:
            self.client = Groq(api_key=self.api_key)
            print(f"[GROQ] Service initialized successfully")
        except Exception as e:
            raise AIServiceError(f"Failed to initialize Groq client: {str(e)}")
    
    @retry_with_fallback(
        max_attempts=Settings.MAX_RETRY_ATTEMPTS,
        delay=Settings.RETRY_DELAY,
        backoff=Settings.RETRY_BACKOFF
    )
    @log_execution
    def complete(
        self,
        system: str,
        user: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Send a completion request to Groq API.
        
        Args:
            system: System prompt
            user: User message
            model: Model to use (defaults to Settings.DEFAULT_MODEL)
            temperature: Temperature for response randomness (0.0-2.0)
            **kwargs: Additional Groq-specific parameters
        
        Returns:
            str: The AI response
        
        Raises:
            AIServiceError: If the request fails after retries
        """
        model = model or Settings.DEFAULT_MODEL
        
        try:
            print(f"[GROQ] Calling API with model: {model}")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=temperature,
                max_tokens=kwargs.get('max_tokens', Settings.MAX_TOKENS),
                **{k: v for k, v in kwargs.items() if k != 'max_tokens'}
            )
            
            result = response.choices[0].message.content.strip()
            print(f"[GROQ] Response received: {len(result)} chars")
            return result
            
        except Exception as e:
            error_msg = f"Groq API error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            raise AIServiceError(error_msg, original_error=e)
    
    @retry_with_fallback(
        max_attempts=Settings.MAX_RETRY_ATTEMPTS,
        delay=Settings.RETRY_DELAY,
        backoff=Settings.RETRY_BACKOFF
    )
    @log_execution
    def complete_json(
        self,
        system: str,
        user: str,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a completion request and parse JSON response.
        
        Args:
            system: System prompt (should instruct to return JSON)
            user: User message
            model: Model to use (defaults to Settings.DEFAULT_MODEL)
            **kwargs: Additional Groq-specific parameters
        
        Returns:
            Dict: Parsed JSON response
        
        Raises:
            AIServiceError: If the request fails or JSON parsing fails
        """
        try:
            response = self.complete(system, user, model=model, temperature=0.3, **kwargs)
            
            # Use safe JSON extraction
            data = safe_json_extract(response)
            
            if not data:
                # Fallback: wrap response in default structure
                print("[GROQ] JSON parsing failed, using fallback structure")
                return {"result": response}
            
            return data
            
        except AIServiceError:
            raise
        except Exception as e:
            raise AIServiceError(f"JSON processing error: {str(e)}", original_error=e)
    
    def is_available(self) -> bool:
        """
        Check if Groq service is available.
        
        Returns:
            bool: True if service is available
        """
        try:
            # Simple test call
            self.complete(
                system="You are a test assistant.",
                user="Say 'OK'",
                model=Settings.DEFAULT_MODEL,
                temperature=0.0
            )
            return True
        except Exception as e:
            print(f"[GROQ] Service unavailable: {str(e)}")
            return False


# Singleton instance for easy import
_groq_service_instance = None

def get_groq_service() -> GroqService:
    """Get singleton Groq service instance"""
    global _groq_service_instance
    if _groq_service_instance is None:
        _groq_service_instance = GroqService()
    return _groq_service_instance
