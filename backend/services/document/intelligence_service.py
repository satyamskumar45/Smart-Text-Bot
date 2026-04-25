"""
Document Intelligence Service
Advanced document analysis with structured extraction:
- Summary (executive, detailed)
- Keywords (ranked by importance)
- Entity recognition (people, organizations, locations, dates, etc.)
- Q&A generation
- Document classification
"""

from typing import Dict, Any, List, Optional
from services.ai.groq_service_refactored import get_groq_service
from core.decorators import log_execution, retry_with_fallback
from core.exceptions import AIServiceError
from utils.output_cleaner import safe_json_extract, ensure_valid_json_response
import json


class DocumentIntelligence:
    """Advanced document analysis and intelligence extraction"""
    
    def __init__(self, ai_service=None):
        self.ai_service = ai_service or get_groq_service()
    
    @log_execution
    @retry_with_fallback(max_attempts=2)
    def analyze_document(
        self,
        text: str,
        include_qa: bool = True,
        max_keywords: int = 10,
        max_entities: int = 20
    ) -> Dict[str, Any]:
        """
        Complete document intelligence analysis.
        
        Args:
            text: Document text
            include_qa: Generate Q&A pairs
            max_keywords: Maximum keywords to extract
            max_entities: Maximum entities to extract
        
        Returns:
            Structured document intelligence
        """
        if not text or len(text.strip()) < 50:
            raise AIServiceError("Text too short for analysis (minimum 50 characters)")
        
        print(f"[DOC_INTEL] Analyzing document: {len(text)} chars")
        
        # Step 1: Extract structured information
        structured_data = self._extract_structured_data(text, max_keywords, max_entities)
        
        # Step 2: Generate Q&A if requested
        if include_qa:
            qa_pairs = self._generate_qa_pairs(text, structured_data)
            structured_data['qa_pairs'] = qa_pairs
        
        # Step 3: Classify document
        classification = self._classify_document(text)
        structured_data['classification'] = classification
        
        # Step 4: Extract metadata
        metadata = self._extract_metadata(text)
        structured_data['metadata'] = metadata
        
        print(f"[DOC_INTEL] Analysis complete")
        return ensure_valid_json_response(structured_data)
    
    def _extract_structured_data(
        self,
        text: str,
        max_keywords: int,
        max_entities: int
    ) -> Dict[str, Any]:
        """Extract summary, keywords, and entities"""
        
        system = self._get_extraction_prompt()
        user = f"""Analyze this document and extract structured information:

TEXT:
{text[:4000]}  

REQUIREMENTS:
- Extract up to {max_keywords} keywords
- Extract up to {max_entities} entities
- Provide both executive and detailed summaries
- Identify key themes and topics

Return ONLY valid JSON following the schema."""

        try:
            response = self.ai_service.complete(system, user, temperature=0.3)
            data = safe_json_extract(response)
            
            if not data:
                raise AIServiceError("Failed to parse structured data")
            
            # Validate and clean
            return self._validate_structured_data(data)
            
        except Exception as e:
            raise AIServiceError(f"Structured extraction failed: {str(e)}")
    
    def _generate_qa_pairs(
        self,
        text: str,
        structured_data: Dict
    ) -> List[Dict[str, str]]:
        """Generate Q&A pairs from document"""
        
        system = """You are an expert at generating insightful questions and answers from documents.

Generate 5-7 question-answer pairs that:
1. Cover key information from the document
2. Are specific and factual
3. Help readers understand the main points
4. Include both simple and complex questions

Return ONLY valid JSON array:
[
  {
    "question": "What is...",
    "answer": "...",
    "difficulty": "easy|medium|hard",
    "category": "factual|conceptual|analytical"
  }
]"""

        # Use summary and keywords for context
        context = f"""SUMMARY: {structured_data.get('summary', {}).get('executive', '')}

KEYWORDS: {', '.join(structured_data.get('keywords', [])[:5])}

FULL TEXT:
{text[:3000]}"""

        try:
            response = self.ai_service.complete(system, context, temperature=0.4)
            qa_data = safe_json_extract(response)
            
            if isinstance(qa_data, list):
                return qa_data[:7]  # Max 7 Q&A pairs
            elif isinstance(qa_data, dict) and 'questions' in qa_data:
                return qa_data['questions'][:7]
            else:
                return []
                
        except Exception as e:
            print(f"[DOC_INTEL] Q&A generation failed: {str(e)}")
            return []
    
    def _classify_document(self, text: str) -> Dict[str, Any]:
        """Classify document type and characteristics"""
        
        system = """Classify the document type and characteristics.

Return ONLY valid JSON:
{
  "type": "article|report|email|letter|contract|invoice|resume|other",
  "domain": "business|technical|legal|medical|academic|general",
  "tone": "formal|informal|neutral|technical",
  "purpose": "informative|persuasive|instructional|transactional",
  "audience": "general|professional|technical|executive",
  "confidence": 0.0-1.0
}"""

        try:
            response = self.ai_service.complete(
                system,
                f"Classify this document:\n\n{text[:1000]}",
                temperature=0.2
            )
            
            classification = safe_json_extract(response)
            return classification if classification else {
                "type": "unknown",
                "domain": "general",
                "tone": "neutral",
                "purpose": "informative",
                "audience": "general",
                "confidence": 0.5
            }
            
        except Exception as e:
            print(f"[DOC_INTEL] Classification failed: {str(e)}")
            return {"type": "unknown", "confidence": 0.0}
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract document metadata"""
        import re
        
        metadata = {
            'word_count': len(text.split()),
            'char_count': len(text),
            'sentence_count': len(re.findall(r'[.!?]+', text)),
            'paragraph_count': len(re.split(r'\n\s*\n', text)),
            'avg_word_length': self._avg_word_length(text),
            'readability_score': self._estimate_readability(text),
        }
        
        # Extract dates
        dates = re.findall(
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            text
        )
        if dates:
            metadata['dates_found'] = dates[:5]
        
        # Extract emails
        emails = re.findall(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            text
        )
        if emails:
            metadata['emails_found'] = emails[:3]
        
        # Extract URLs
        urls = re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            text
        )
        if urls:
            metadata['urls_found'] = urls[:3]
        
        return metadata
    
    def _avg_word_length(self, text: str) -> float:
        """Calculate average word length"""
        words = text.split()
        if not words:
            return 0.0
        return round(sum(len(word) for word in words) / len(words), 2)
    
    def _estimate_readability(self, text: str) -> str:
        """Estimate readability level"""
        avg_word_len = self._avg_word_length(text)
        
        if avg_word_len < 4.5:
            return "easy"
        elif avg_word_len < 5.5:
            return "moderate"
        else:
            return "difficult"
    
    def _validate_structured_data(self, data: Dict) -> Dict:
        """Validate and ensure all required fields exist"""
        
        # Ensure summary exists
        if 'summary' not in data:
            data['summary'] = {}
        
        if not isinstance(data['summary'], dict):
            data['summary'] = {'executive': str(data['summary'])}
        
        if 'executive' not in data['summary']:
            data['summary']['executive'] = "Summary not available"
        
        if 'detailed' not in data['summary']:
            data['summary']['detailed'] = data['summary']['executive']
        
        # Ensure keywords exist
        if 'keywords' not in data or not isinstance(data['keywords'], list):
            data['keywords'] = []
        
        # Ensure entities exist
        if 'entities' not in data:
            data['entities'] = {}
        
        # Ensure themes exist
        if 'themes' not in data or not isinstance(data['themes'], list):
            data['themes'] = []
        
        # Ensure key_points exist
        if 'key_points' not in data or not isinstance(data['key_points'], list):
            data['key_points'] = []
        
        return data
    
    def _get_extraction_prompt(self) -> str:
        """Get the structured extraction prompt"""
        return """You are an expert document analyst. Extract structured information from documents.

Return ONLY valid JSON in this EXACT format:
{
  "summary": {
    "executive": "1-2 sentence high-level summary for executives",
    "detailed": "3-4 sentence comprehensive summary covering main points"
  },
  "keywords": [
    {
      "term": "keyword or phrase",
      "relevance": 0.0-1.0,
      "category": "topic|concept|technology|person|organization|location"
    }
  ],
  "entities": {
    "people": ["Person Name 1", "Person Name 2"],
    "organizations": ["Company 1", "Organization 2"],
    "locations": ["City", "Country"],
    "dates": ["2024-01-15", "March 2024"],
    "technologies": ["Technology 1", "Tool 2"],
    "products": ["Product 1", "Service 2"],
    "monetary": ["$1000", "€500"]
  },
  "themes": [
    {
      "theme": "Main theme or topic",
      "description": "Brief explanation",
      "importance": 0.0-1.0
    }
  ],
  "key_points": [
    "First key point or finding",
    "Second key point or finding",
    "Third key point or finding"
  ],
  "sentiment": {
    "overall": "positive|negative|neutral|mixed",
    "confidence": 0.0-1.0,
    "aspects": {
      "tone": "professional|casual|technical|emotional",
      "urgency": "high|medium|low"
    }
  }
}

IMPORTANT:
- Extract ONLY information present in the text
- Rank keywords by relevance (most important first)
- Group entities by type
- Identify 3-5 main themes
- Extract 5-7 key points
- Be precise and factual"""


# =========================
# CONVENIENCE FUNCTIONS
# =========================

def analyze_document(
    text: str,
    include_qa: bool = True,
    max_keywords: int = 10
) -> Dict[str, Any]:
    """
    Quick document analysis.
    
    Args:
        text: Document text
        include_qa: Generate Q&A pairs
        max_keywords: Maximum keywords
    
    Returns:
        Structured document intelligence
    """
    service = DocumentIntelligence()
    return service.analyze_document(text, include_qa, max_keywords)
