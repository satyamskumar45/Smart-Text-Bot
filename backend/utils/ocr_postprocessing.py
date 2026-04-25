"""
Advanced OCR Text Cleanup and Post-Processing
Cleans and structures raw OCR output.
"""

import re
from typing import List, Dict, Tuple
from collections import Counter


class OCRTextCleaner:
    """Advanced OCR text cleanup and correction"""
    
    def __init__(self):
        # Common OCR character mistakes
        self.char_corrections = {
            # Numbers mistaken for letters
            '0': {'O', 'o', 'D'},
            '1': {'l', 'I', '|', 'i'},
            '2': {'Z', 'z'},
            '3': {'E'},
            '5': {'S', 's'},
            '6': {'G', 'b'},
            '8': {'B'},
            '9': {'g', 'q'},
            
            # Letters mistaken for numbers
            'O': {'0'},
            'o': {'0'},
            'l': {'1', 'I'},
            'I': {'1', 'l'},
            'S': {'5'},
            's': {'5'},
            'Z': {'2'},
            'B': {'8'},
            
            # Special characters
            '©': 'c',
            '®': 'r',
            '™': 'tm',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY',
        }
        
        # Common OCR word mistakes
        self.word_corrections = {
            'tlie': 'the',
            'tbe': 'the',
            'witli': 'with',
            'wliich': 'which',
            'wlien': 'when',
            'wliere': 'where',
            'wlio': 'who',
            'wliat': 'what',
            'wliy': 'why',
            'liave': 'have',
            'liad': 'had',
            'lias': 'has',
            'tliis': 'this',
            'tliat': 'that',
            'tliese': 'these',
            'tliose': 'those',
        }
    
    def clean(self, text: str, aggressive: bool = False) -> str:
        """
        Complete OCR text cleaning pipeline.
        
        Args:
            text: Raw OCR text
            aggressive: Use aggressive cleaning
        
        Returns:
            Cleaned text
        """
        if not text or not text.strip():
            return ""
        
        # 1. Fix encoding issues
        text = self._fix_encoding(text)
        
        # 2. Remove control characters
        text = self._remove_control_chars(text)
        
        # 3. Fix broken words across lines
        text = self._fix_hyphenation(text)
        
        # 4. Fix spacing issues
        text = self._fix_spacing(text)
        
        # 5. Fix common OCR mistakes
        text = self._fix_common_mistakes(text)
        
        # 6. Remove isolated special characters
        text = self._remove_isolated_chars(text)
        
        # 7. Fix punctuation
        text = self._fix_punctuation(text)
        
        # 8. Remove excessive whitespace
        text = self._normalize_whitespace(text)
        
        if aggressive:
            # 9. Remove very short lines (likely noise)
            text = self._remove_short_lines(text, min_length=3)
            
            # 10. Remove lines with too many special chars
            text = self._remove_noisy_lines(text)
        
        return text.strip()
    
    def _fix_encoding(self, text: str) -> str:
        """Fix common encoding issues"""
        replacements = {
            'â€™': "'",
            'â€œ': '"',
            'â€': '"',
            'â€"': '—',
            'â€"': '–',
            'Ã©': 'é',
            'Ã¨': 'è',
            'Ã ': 'à',
            'Ã§': 'ç',
        }
        
        for wrong, right in replacements.items():
            text = text.replace(wrong, right)
        
        return text
    
    def _remove_control_chars(self, text: str) -> str:
        """Remove control characters except newlines and tabs"""
        return re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    def _fix_hyphenation(self, text: str) -> str:
        """Fix words broken across lines with hyphens"""
        # Match word-\nword pattern
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Match word-\r\nword pattern
        text = re.sub(r'(\w+)-\s*\r?\n\s*(\w+)', r'\1\2', text)
        
        return text
    
    def _fix_spacing(self, text: str) -> str:
        """Fix spacing issues"""
        # Remove spaces before punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Add space after punctuation if missing
        text = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', text)
        
        # Fix multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Fix space at start of line
        text = re.sub(r'\n +', '\n', text)
        
        return text
    
    def _fix_common_mistakes(self, text: str) -> str:
        """Fix common OCR word mistakes"""
        words = text.split()
        corrected = []
        
        for word in words:
            # Check if word needs correction
            lower_word = word.lower()
            if lower_word in self.word_corrections:
                # Preserve original case
                if word.isupper():
                    corrected.append(self.word_corrections[lower_word].upper())
                elif word[0].isupper():
                    corrected.append(self.word_corrections[lower_word].capitalize())
                else:
                    corrected.append(self.word_corrections[lower_word])
            else:
                corrected.append(word)
        
        return ' '.join(corrected)
    
    def _remove_isolated_chars(self, text: str) -> str:
        """Remove isolated single characters (likely noise)"""
        # Remove isolated special characters
        text = re.sub(r'\s[^\w\s.,!?;:()\[\]{}"\'-]\s', ' ', text)
        
        # Remove isolated single letters (except 'a', 'I')
        text = re.sub(r'\s[b-hj-z]\s', ' ', text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_punctuation(self, text: str) -> str:
        """Fix punctuation issues"""
        # Fix multiple punctuation marks
        text = re.sub(r'\.{2,}', '...', text)  # Multiple dots to ellipsis
        text = re.sub(r'!{2,}', '!', text)
        text = re.sub(r'\?{2,}', '?', text)
        
        # Fix comma spacing
        text = re.sub(r',([^\s\d])', r', \1', text)
        
        # Fix quotes
        text = re.sub(r'``', '"', text)
        text = re.sub(r"''", '"', text)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace"""
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Fix multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Fix multiple newlines (keep max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing whitespace from lines
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        text = '\n'.join(lines)
        
        return text
    
    def _remove_short_lines(self, text: str, min_length: int = 3) -> str:
        """Remove very short lines (likely noise)"""
        lines = text.split('\n')
        cleaned = []
        
        for line in lines:
            # Keep line if it has enough words
            words = line.split()
            if len(words) >= min_length or len(line.strip()) > 20:
                cleaned.append(line)
        
        return '\n'.join(cleaned)
    
    def _remove_noisy_lines(self, text: str, threshold: float = 0.3) -> str:
        """Remove lines with too many special characters"""
        lines = text.split('\n')
        cleaned = []
        
        for line in lines:
            if not line.strip():
                cleaned.append(line)
                continue
            
            # Count special characters
            special_count = len(re.findall(r'[^\w\s.,!?;:()\[\]{}"\'-]', line))
            total_chars = len(line.strip())
            
            if total_chars == 0:
                continue
            
            # Keep line if special char ratio is below threshold
            if special_count / total_chars < threshold:
                cleaned.append(line)
        
        return '\n'.join(cleaned)
    
    def detect_language_patterns(self, text: str) -> Dict[str, float]:
        """Detect language patterns to help with cleaning"""
        patterns = {
            'has_numbers': bool(re.search(r'\d', text)),
            'has_uppercase': bool(re.search(r'[A-Z]', text)),
            'has_lowercase': bool(re.search(r'[a-z]', text)),
            'avg_word_length': self._avg_word_length(text),
            'punctuation_ratio': self._punctuation_ratio(text),
        }
        
        return patterns
    
    def _avg_word_length(self, text: str) -> float:
        """Calculate average word length"""
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return 0.0
        return sum(len(word) for word in words) / len(words)
    
    def _punctuation_ratio(self, text: str) -> float:
        """Calculate punctuation ratio"""
        if not text:
            return 0.0
        punct_count = len(re.findall(r'[.,!?;:]', text))
        return punct_count / len(text)


class OCRTextReconstructor:
    """Reconstruct document structure from OCR text"""
    
    def __init__(self):
        self.cleaner = OCRTextCleaner()
    
    def reconstruct(self, text: str) -> Dict[str, any]:
        """
        Reconstruct document structure.
        
        Args:
            text: Cleaned OCR text
        
        Returns:
            Dict with structured content
        """
        # Clean first
        text = self.cleaner.clean(text)
        
        # Detect structure
        structure = {
            'title': self._extract_title(text),
            'paragraphs': self._extract_paragraphs(text),
            'lists': self._extract_lists(text),
            'headings': self._extract_headings(text),
            'metadata': self._extract_metadata(text),
        }
        
        return structure
    
    def _extract_title(self, text: str) -> str:
        """Extract document title (usually first line or all caps)"""
        lines = text.split('\n')
        
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if not line:
                continue
            
            # Title is often all caps or first substantial line
            if line.isupper() and len(line) > 10:
                return line
            
            # Or first line with enough words
            if len(line.split()) >= 3:
                return line
        
        return ""
    
    def _extract_paragraphs(self, text: str) -> List[str]:
        """Extract paragraphs from text"""
        # Split by double newlines
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Clean and filter
        cleaned = []
        for para in paragraphs:
            para = para.strip()
            
            # Skip very short paragraphs
            if len(para.split()) < 5:
                continue
            
            # Skip if looks like a list item
            if re.match(r'^[\d•\-*]\s', para):
                continue
            
            cleaned.append(para)
        
        return cleaned
    
    def _extract_lists(self, text: str) -> List[List[str]]:
        """Extract lists from text"""
        lines = text.split('\n')
        lists = []
        current_list = []
        
        for line in lines:
            line = line.strip()
            
            # Check if line is a list item
            if re.match(r'^[\d•\-*]\s', line):
                # Remove list marker
                item = re.sub(r'^[\d•\-*]\s+', '', line)
                current_list.append(item)
            else:
                # End of list
                if current_list:
                    lists.append(current_list)
                    current_list = []
        
        # Add last list
        if current_list:
            lists.append(current_list)
        
        return lists
    
    def _extract_headings(self, text: str) -> List[str]:
        """Extract headings from text"""
        lines = text.split('\n')
        headings = []
        
        for line in lines:
            line = line.strip()
            
            # Headings are often:
            # - All caps
            # - Short (< 10 words)
            # - Not ending with punctuation
            
            if not line:
                continue
            
            words = line.split()
            
            if (line.isupper() or 
                (len(words) <= 10 and not line[-1] in '.,!?;:')):
                headings.append(line)
        
        return headings
    
    def _extract_metadata(self, text: str) -> Dict[str, str]:
        """Extract metadata (dates, page numbers, etc.)"""
        metadata = {}
        
        # Extract dates
        dates = re.findall(
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            text
        )
        if dates:
            metadata['dates'] = dates
        
        # Extract page numbers
        pages = re.findall(r'\bPage\s+\d+\b|\b\d+\s+of\s+\d+\b', text, re.IGNORECASE)
        if pages:
            metadata['pages'] = pages
        
        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            metadata['emails'] = emails
        
        # Extract phone numbers
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        if phones:
            metadata['phones'] = phones
        
        return metadata
    
    def format_as_markdown(self, structure: Dict) -> str:
        """Format structured content as Markdown"""
        md = []
        
        # Title
        if structure.get('title'):
            md.append(f"# {structure['title']}\n")
        
        # Paragraphs
        for para in structure.get('paragraphs', []):
            md.append(f"{para}\n")
        
        # Lists
        for lst in structure.get('lists', []):
            for item in lst:
                md.append(f"- {item}")
            md.append("")
        
        return '\n'.join(md)


# =========================
# CONVENIENCE FUNCTIONS
# =========================

def clean_ocr_text(text: str, aggressive: bool = False) -> str:
    """Quick OCR text cleaning"""
    cleaner = OCRTextCleaner()
    return cleaner.clean(text, aggressive=aggressive)


def reconstruct_document(text: str) -> Dict:
    """Quick document reconstruction"""
    reconstructor = OCRTextReconstructor()
    return reconstructor.reconstruct(text)
