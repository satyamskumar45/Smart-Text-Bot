"""
Base AI Service - Abstract interface for AI providers.
Allows easy switching between different AI services (Groq, OpenAI, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAIService(ABC):
    """Abstract base class for AI services"""
    
    @abstractmethod
    def complete(
        self,
        system: str,
        user: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Send a completion request to the AI service.
        
        Args:
            system: System prompt
            user: User message
            model: Model to use (provider-specific)
            temperature: Temperature for response randomness (0.0-2.0)
            **kwargs: Additional provider-specific parameters
        
        Returns:
            str: The AI response
        
        Raises:
            AIServiceError: If the request fails
        """
        pass
    
    @abstractmethod
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
            system: System prompt
            user: User message
            model: Model to use (provider-specific)
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Dict: Parsed JSON response
        
        Raises:
            AIServiceError: If the request fails or JSON parsing fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the AI service is available.
        
        Returns:
            bool: True if service is available, False otherwise
        """
        pass
    
    def get_provider_name(self) -> str:
        """Get the name of the AI provider"""
        return self.__class__.__name__.replace('Service', '')
