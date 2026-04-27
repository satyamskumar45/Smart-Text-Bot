"""
OCR Service - Complete OCR pipeline with preprocessing and postprocessing.
Integrates image enhancement, OCR extraction, and text cleanup.
"""

import os
import shutil
import pytesseract
from PIL import Image
import io
from typing import Dict, Any, Optional, Tuple
from config.settings import Settings
from core.exceptions import OCRError
from core.decorators import retry_with_fallback, log_execution
from utils.ocr_preprocessing import OCRPreprocessor, preprocess_for_ocr
from utils.ocr_postprocessing import OCRTextCleaner, OCRTextReconstructor


class OCRService:
    """Complete OCR service with preprocessing and postprocessing"""
    
    def __init__(self):
        """Initialize OCR service"""
        self.tesseract_cmd = self._resolve_tesseract_cmd()
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        self.preprocessor = OCRPreprocessor()
        self.cleaner = OCRTextCleaner()
        self.reconstructor = OCRTextReconstructor()

    def _resolve_tesseract_cmd(self) -> Optional[str]:
        """Resolve the best available Tesseract executable path for the current environment."""
        configured_path = (Settings.TESSERACT_PATH or "").strip()
        if configured_path:
            return configured_path

        path_binary = shutil.which("tesseract")
        if path_binary:
            return path_binary

        windows_fallback = (Settings.TESSERACT_WINDOWS_FALLBACK or "").strip()
        if Settings.is_windows() and windows_fallback and os.path.exists(windows_fallback):
            return windows_fallback

        return None

    def is_available(self) -> bool:
        """Check whether Tesseract is available in the current runtime."""
        return bool(self._resolve_tesseract_cmd())

    def get_unavailable_message(self) -> str:
        """Return a production-safe message when OCR runtime dependencies are unavailable."""
        return (
            "OCR is currently unavailable because the Tesseract runtime is not installed on this server. "
            "Please install Tesseract or configure the TESSERACT_PATH environment variable."
        )

    def ensure_available(self):
        """Raise a clean OCR error when Tesseract is unavailable."""
        resolved_cmd = self._resolve_tesseract_cmd()
        if not resolved_cmd:
            raise OCRError(self.get_unavailable_message())

        self.tesseract_cmd = resolved_cmd
        pytesseract.pytesseract.tesseract_cmd = resolved_cmd
    
    @retry_with_fallback(max_attempts=2)
    @log_execution
    def extract_text(
        self,
        image_bytes: bytes,
        preprocess_method: str = "auto",
        clean_aggressive: bool = False,
        lang: str = "eng"
    ) -> Dict[str, Any]:
        """
        Extract text from image with full pipeline.
        
        Args:
            image_bytes: Raw image bytes
            preprocess_method: "auto", "standard", "aggressive", "light"
            clean_aggressive: Use aggressive text cleaning
            lang: Tesseract language code
        
        Returns:
            Dict with extracted text and metadata
        
        Raises:
            OCRError: If OCR fails
        """
        try:
            self.ensure_available()

            # Step 1: Preprocess image
            print(f"[OCR] Preprocessing image with method: {preprocess_method}")
            original, preprocessed = self.preprocessor.enhance_for_ocr(
                image_bytes,
                method=preprocess_method
            )
            
            # Step 2: Extract text with Tesseract
            print(f"[OCR] Extracting text with Tesseract (lang={lang})")
            raw_text = pytesseract.image_to_string(preprocessed, lang=lang)
            
            if not raw_text.strip():
                # Fallback: Try with original image
                print("[OCR] No text found, trying with original image")
                raw_text = pytesseract.image_to_string(original, lang=lang)
                
                if not raw_text.strip():
                    raise OCRError("No text detected in image")
            
            # Step 3: Clean text
            print(f"[OCR] Cleaning text (aggressive={clean_aggressive})")
            cleaned_text = self.cleaner.clean(raw_text, aggressive=clean_aggressive)
            
            # Step 4: Reconstruct structure
            print("[OCR] Reconstructing document structure")
            structure = self.reconstructor.reconstruct(cleaned_text)
            
            # Step 5: Get confidence (if available)
            confidence = self._get_confidence(preprocessed, lang)
            
            result = {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'structure': structure,
                'confidence': confidence,
                'char_count': len(cleaned_text),
                'word_count': len(cleaned_text.split()),
                'preprocessing_method': preprocess_method,
            }
            
            print(f"[OCR] Extraction complete: {result['word_count']} words, {confidence}% confidence")
            return result
            
        except pytesseract.TesseractNotFoundError:
            raise OCRError(self.get_unavailable_message())
        except Exception as e:
            raise OCRError(f"OCR extraction failed: {str(e)}")
    
    def extract_text_simple(
        self,
        image_bytes: bytes,
        preprocess: bool = True
    ) -> str:
        """
        Simple text extraction (just returns cleaned text).
        
        Args:
            image_bytes: Raw image bytes
            preprocess: Apply preprocessing
        
        Returns:
            Cleaned text string
        """
        try:
            self.ensure_available()

            if preprocess:
                image = preprocess_for_ocr(image_bytes)
            else:
                image = Image.open(io.BytesIO(image_bytes))
            
            raw_text = pytesseract.image_to_string(image)
            
            if not raw_text.strip():
                raise OCRError("No text detected")
            
            return self.cleaner.clean(raw_text)
            
        except pytesseract.TesseractNotFoundError:
            raise OCRError(self.get_unavailable_message())
        except Exception as e:
            raise OCRError(f"OCR failed: {str(e)}")
    
    def extract_with_fallback(
        self,
        image_bytes: bytes
    ) -> Tuple[str, str]:
        """
        Extract text with multiple fallback strategies.
        
        Args:
            image_bytes: Raw image bytes
        
        Returns:
            Tuple of (text, method_used)
        """
        strategies = [
            ("auto", False),
            ("aggressive", False),
            ("standard", True),
            ("light", True),
        ]
        
        last_error = None
        
        for method, aggressive in strategies:
            try:
                print(f"[OCR] Trying method: {method}, aggressive={aggressive}")
                result = self.extract_text(
                    image_bytes,
                    preprocess_method=method,
                    clean_aggressive=aggressive
                )
                return result['cleaned_text'], method
            except Exception as e:
                last_error = e
                continue
        
        raise OCRError(f"All OCR strategies failed. Last error: {str(last_error)}")
    
    def _get_confidence(self, image: Image.Image, lang: str = "eng") -> float:
        """Get OCR confidence score"""
        try:
            self.ensure_available()
            # Get detailed data from Tesseract
            data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                return round(sum(confidences) / len(confidences), 2)
            else:
                return 0.0
        except:
            return 0.0
    
    def compare_methods(
        self,
        image_bytes: bytes
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare different preprocessing methods.
        
        Args:
            image_bytes: Raw image bytes
        
        Returns:
            Dict with results from each method
        """
        methods = ["light", "standard", "aggressive"]
        results = {}
        
        for method in methods:
            try:
                result = self.extract_text(
                    image_bytes,
                    preprocess_method=method,
                    clean_aggressive=False
                )
                results[method] = {
                    'word_count': result['word_count'],
                    'confidence': result['confidence'],
                    'preview': result['cleaned_text'][:200]
                }
            except Exception as e:
                results[method] = {'error': str(e)}
        
        return results


# =========================
# CONVENIENCE FUNCTIONS
# =========================

def extract_text_from_image(
    image_bytes: bytes,
    preprocess: bool = True,
    clean: bool = True
) -> str:
    """
    Quick text extraction from image.
    
    Args:
        image_bytes: Raw image bytes
        preprocess: Apply image preprocessing
        clean: Apply text cleaning
    
    Returns:
        Extracted text
    """
    service = OCRService()
    service.ensure_available()
    
    if preprocess and clean:
        return service.extract_text_simple(image_bytes, preprocess=True)
    elif preprocess:
        image = preprocess_for_ocr(image_bytes)
        return pytesseract.image_to_string(image)
    else:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        if clean:
            cleaner = OCRTextCleaner()
            return cleaner.clean(text)
        return text
