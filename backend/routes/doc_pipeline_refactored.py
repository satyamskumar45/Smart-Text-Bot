"""
Document Pipeline Routes - Refactored with advanced OCR processing.
"""

from flask import Blueprint, request
from services.document.ocr_service import OCRService
from services.text.translation_service import TranslationService
from services.text.summarization_service import SummarizationService
from utils.response import success, error
from core.exceptions import OCRError, ValidationError, AIServiceError
from core.decorators import log_execution

doc_pipeline_bp = Blueprint('doc_pipeline', __name__)

# Initialize services
ocr_service = OCRService()
translation_service = TranslationService()


@doc_pipeline_bp.route('/pipeline', methods=['POST'])
@log_execution
def pipeline():
    """
    Complete document processing pipeline.
    
    Request:
        - file: Image file (multipart/form-data)
        - target_lang: Target language (optional, default: en)
        - preprocess_method: auto/standard/aggressive/light (optional)
        - clean_aggressive: true/false (optional)
    
    Response:
        {
            "success": true,
            "data": {
                "extracted_text": "...",
                "cleaned_text": "...",
                "structure": {...},
                "translation": "...",
                "summary": "...",
                "bullets": [...],
                "metadata": {...}
            }
        }
    """
    try:
        # Validate input
        file = request.files.get('file')
        if not file:
            raise ValidationError("No file uploaded")
        
        target_lang = request.form.get('target_lang', 'en')
        preprocess_method = request.form.get('preprocess_method', 'auto')
        clean_aggressive = request.form.get('clean_aggressive', 'false').lower() == 'true'
        
        print("\n🚀 DOCUMENT PIPELINE STARTED")
        print(f"   Target Language: {target_lang}")
        print(f"   Preprocess Method: {preprocess_method}")
        print(f"   Aggressive Cleaning: {clean_aggressive}")
        
        # =========================
        # STEP 1: OCR EXTRACTION
        # =========================
        print("\n📄 STEP 1: OCR Extraction")
        try:
            image_bytes = file.read()
            ocr_result = ocr_service.extract_text(
                image_bytes,
                preprocess_method=preprocess_method,
                clean_aggressive=clean_aggressive
            )
            
            extracted_text = ocr_result['cleaned_text']
            structure = ocr_result['structure']
            
            print(f"✅ OCR Complete:")
            print(f"   - Words: {ocr_result['word_count']}")
            print(f"   - Confidence: {ocr_result['confidence']}%")
            print(f"   - Method: {ocr_result['preprocessing_method']}")
            
        except OCRError as e:
            print(f"❌ OCR Failed: {str(e)}")
            return error(f"OCR extraction failed: {str(e)}", 500)
        
        # =========================
        # STEP 2: TRANSLATION
        # =========================
        print("\n🌍 STEP 2: Translation")
        translated_text = extracted_text
        
        if target_lang.lower() not in ['en', 'english']:
            try:
                translation_result = translation_service.translate(
                    text=extracted_text,
                    target_lang=target_lang,
                    source_lang='auto'
                )
                translated_text = translation_result['translated_text']
                print(f"✅ Translation Complete: {target_lang}")
            except Exception as e:
                print(f"⚠️ Translation Failed: {str(e)}")
                # Continue with original text
        else:
            print("⏭️ Translation Skipped (target is English)")
        
        # =========================
        # STEP 3: SUMMARIZATION
        # =========================
        print("\n📝 STEP 3: Summarization")
        summary = ""
        bullets = []
        
        try:
            # Use summarization service (to be created)
            from services.groq_service import complete
            from utils.output_cleaner import format_summary, extract_bullet_points, safe_json_extract
            
            system = (
                "You are an expert summarizer. "
                "Return ONLY JSON: "
                '{"paragraph": "2-3 line summary", "bullets": ["point1", "point2"]}'
            )
            user = f"Summarize this:\n\n{translated_text}"
            
            response = complete(system, user, temperature=0.4)
            data = safe_json_extract(response)
            
            if data:
                summary = format_summary(data.get('paragraph', ''))
                bullets = data.get('bullets', [])
                if not bullets:
                    bullets = extract_bullet_points(response)
            else:
                summary = format_summary(response)
            
            print(f"✅ Summarization Complete:")
            print(f"   - Summary: {len(summary)} chars")
            print(f"   - Bullets: {len(bullets)} points")
            
        except Exception as e:
            print(f"⚠️ Summarization Failed: {str(e)}")
            summary = "Summary generation failed"
        
        # =========================
        # STEP 4: BUILD RESPONSE
        # =========================
        print("\n✨ STEP 4: Building Response")
        
        result = {
            'extracted_text': extracted_text,
            'cleaned_text': extracted_text,
            'structure': structure,
            'translation': translated_text,
            'summary': summary,
            'bullets': bullets,
            'metadata': {
                'word_count': ocr_result['word_count'],
                'char_count': ocr_result['char_count'],
                'confidence': ocr_result['confidence'],
                'preprocessing_method': ocr_result['preprocessing_method'],
                'target_language': target_lang,
            }
        }
        
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY\n")
        return success(result)
        
    except ValidationError as e:
        print(f"❌ Validation Error: {str(e)}")
        return error(str(e), 400)
    except OCRError as e:
        print(f"❌ OCR Error: {str(e)}")
        return error(str(e), 500)
    except Exception as e:
        print(f"❌ Pipeline Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f"Pipeline failed: {str(e)}", 500)


@doc_pipeline_bp.route('/ocr', methods=['POST'])
def ocr_only():
    """
    OCR extraction only (no translation or summarization).
    
    Request:
        - file: Image file
        - preprocess_method: auto/standard/aggressive/light (optional)
        - clean_aggressive: true/false (optional)
    
    Response:
        {
            "success": true,
            "data": {
                "raw_text": "...",
                "cleaned_text": "...",
                "structure": {...},
                "metadata": {...}
            }
        }
    """
    try:
        file = request.files.get('file')
        if not file:
            raise ValidationError("No file uploaded")
        
        preprocess_method = request.form.get('preprocess_method', 'auto')
        clean_aggressive = request.form.get('clean_aggressive', 'false').lower() == 'true'
        
        image_bytes = file.read()
        result = ocr_service.extract_text(
            image_bytes,
            preprocess_method=preprocess_method,
            clean_aggressive=clean_aggressive
        )
        
        return success({
            'raw_text': result['raw_text'],
            'cleaned_text': result['cleaned_text'],
            'structure': result['structure'],
            'metadata': {
                'word_count': result['word_count'],
                'char_count': result['char_count'],
                'confidence': result['confidence'],
                'preprocessing_method': result['preprocessing_method'],
            }
        })
        
    except ValidationError as e:
        return error(str(e), 400)
    except OCRError as e:
        return error(str(e), 500)


@doc_pipeline_bp.route('/ocr/compare', methods=['POST'])
def compare_methods():
    """
    Compare different OCR preprocessing methods.
    
    Request:
        - file: Image file
    
    Response:
        {
            "success": true,
            "data": {
                "light": {...},
                "standard": {...},
                "aggressive": {...}
            }
        }
    """
    try:
        file = request.files.get('file')
        if not file:
            raise ValidationError("No file uploaded")
        
        image_bytes = file.read()
        results = ocr_service.compare_methods(image_bytes)
        
        return success(results)
        
    except ValidationError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Comparison failed: {str(e)}", 500)


@doc_pipeline_bp.route('/ocr/fallback', methods=['POST'])
def ocr_with_fallback():
    """
    OCR extraction with automatic fallback strategies.
    
    Request:
        - file: Image file
    
    Response:
        {
            "success": true,
            "data": {
                "text": "...",
                "method_used": "..."
            }
        }
    """
    try:
        file = request.files.get('file')
        if not file:
            raise ValidationError("No file uploaded")
        
        image_bytes = file.read()
        text, method = ocr_service.extract_with_fallback(image_bytes)
        
        return success({
            'text': text,
            'method_used': method,
            'word_count': len(text.split())
        })
        
    except ValidationError as e:
        return error(str(e), 400)
    except OCRError as e:
        return error(str(e), 500)
