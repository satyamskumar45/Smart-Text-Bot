"""
Complete Document Pipeline - Integrated OCR and Intelligence
Combines OCR extraction with advanced document intelligence.
"""

from flask import Blueprint, request
from services.document.ocr_service import OCRService
from services.document.intelligence_service import DocumentIntelligence
from services.text.translation_service import TranslationService
from utils.response import success, error
from core.exceptions import OCRError, ValidationError, AIServiceError
from core.decorators import log_execution
from utils.output_cleaner import ensure_valid_json_response

doc_pipeline_complete_bp = Blueprint('doc_pipeline_complete', __name__)

# Initialize services
ocr_service = OCRService()
intelligence_service = DocumentIntelligence()
translation_service = TranslationService()


@doc_pipeline_complete_bp.route('/document/analyze', methods=['POST'])
@log_execution
def analyze_document():
    """
    Complete document analysis pipeline with intelligence.
    
    Request (multipart/form-data):
        - file: Image file (required)
        - target_lang: Target language (optional, default: en)
        - preprocess_method: auto/light/standard/aggressive (optional, default: auto)
        - include_qa: true/false (optional, default: true)
        - max_keywords: int (optional, default: 10)
    
    Response:
        {
            "success": true,
            "data": {
                "ocr": {
                    "extracted_text": "...",
                    "confidence": 92.5,
                    "structure": {...}
                },
                "intelligence": {
                    "summary": {...},
                    "keywords": [...],
                    "entities": {...},
                    "themes": [...],
                    "key_points": [...],
                    "sentiment": {...},
                    "qa_pairs": [...],
                    "classification": {...}
                },
                "translation": {
                    "translated_text": "...",
                    "target_lang": "es"
                },
                "metadata": {...}
            }
        }
    """
    try:
        # =========================
        # STEP 1: VALIDATE INPUT
        # =========================
        file = request.files.get('file')
        if not file:
            raise ValidationError("No file uploaded")
        
        target_lang = request.form.get('target_lang', 'en')
        preprocess_method = request.form.get('preprocess_method', 'auto')
        include_qa = request.form.get('include_qa', 'true').lower() == 'true'
        max_keywords = int(request.form.get('max_keywords', '10'))
        
        print("\n" + "="*60)
        print("🚀 COMPLETE DOCUMENT ANALYSIS PIPELINE")
        print("="*60)
        print(f"📋 Configuration:")
        print(f"   - Target Language: {target_lang}")
        print(f"   - Preprocess Method: {preprocess_method}")
        print(f"   - Include Q&A: {include_qa}")
        print(f"   - Max Keywords: {max_keywords}")
        print("="*60)
        
        # =========================
        # STEP 2: OCR EXTRACTION
        # =========================
        print("\n📄 STEP 1/4: OCR Extraction")
        print("-" * 40)
        
        try:
            image_bytes = file.read()
            ocr_result = ocr_service.extract_text(
                image_bytes,
                preprocess_method=preprocess_method,
                clean_aggressive=False
            )
            
            extracted_text = ocr_result['cleaned_text']
            
            print(f"✅ OCR Complete:")
            print(f"   - Words: {ocr_result['word_count']}")
            print(f"   - Confidence: {ocr_result['confidence']}%")
            print(f"   - Method: {ocr_result['preprocessing_method']}")
            
        except OCRError as e:
            print(f"❌ OCR Failed: {str(e)}")
            return error(f"OCR extraction failed: {str(e)}", 500)
        
        # =========================
        # STEP 3: DOCUMENT INTELLIGENCE
        # =========================
        print("\n🧠 STEP 2/4: Document Intelligence")
        print("-" * 40)
        
        try:
            intelligence_result = intelligence_service.analyze_document(
                text=extracted_text,
                include_qa=include_qa,
                max_keywords=max_keywords
            )
            
            print(f"✅ Intelligence Analysis Complete:")
            print(f"   - Keywords: {len(intelligence_result.get('keywords', []))}")
            print(f"   - Entities: {sum(len(v) if isinstance(v, list) else 0 for v in intelligence_result.get('entities', {}).values())}")
            print(f"   - Themes: {len(intelligence_result.get('themes', []))}")
            print(f"   - Key Points: {len(intelligence_result.get('key_points', []))}")
            if include_qa:
                print(f"   - Q&A Pairs: {len(intelligence_result.get('qa_pairs', []))}")
            
        except AIServiceError as e:
            print(f"⚠️ Intelligence Analysis Failed: {str(e)}")
            # Continue with basic analysis
            intelligence_result = {
                "summary": {
                    "executive": "Analysis failed",
                    "detailed": str(e)
                },
                "keywords": [],
                "entities": {},
                "themes": [],
                "key_points": [],
                "sentiment": {"overall": "neutral", "confidence": 0.0}
            }
        
        # =========================
        # STEP 4: TRANSLATION
        # =========================
        print("\n🌍 STEP 3/4: Translation")
        print("-" * 40)
        
        translated_text = extracted_text
        translation_result = None
        
        if target_lang.lower() not in ['en', 'english']:
            try:
                translation_result = translation_service.translate(
                    text=extracted_text,
                    target_lang=target_lang,
                    source_lang='auto'
                )
                translated_text = translation_result['translated_text']
                
                print(f"✅ Translation Complete:")
                print(f"   - Target: {target_lang}")
                print(f"   - Words: {len(translated_text.split())}")
                
            except Exception as e:
                print(f"⚠️ Translation Failed: {str(e)}")
                translation_result = None
        else:
            print("⏭️ Translation Skipped (target is English)")
        
        # =========================
        # STEP 5: BUILD RESPONSE
        # =========================
        print("\n✨ STEP 4/4: Building Response")
        print("-" * 40)
        
        response_data = {
            'ocr': {
                'extracted_text': extracted_text,
                'confidence': ocr_result['confidence'],
                'word_count': ocr_result['word_count'],
                'preprocessing_method': ocr_result['preprocessing_method'],
                'structure': ocr_result.get('structure', {})
            },
            'intelligence': intelligence_result,
            'metadata': {
                **ocr_result.get('metadata', {}),
                **intelligence_result.get('metadata', {}),
                'target_language': target_lang,
                'analysis_complete': True
            }
        }
        
        # Add translation if performed
        if translation_result:
            response_data['translation'] = {
                'translated_text': translated_text,
                'source_lang': translation_result.get('source_lang', 'auto'),
                'target_lang': target_lang
            }
        
        # Ensure UI-safe output
        response_data = ensure_valid_json_response(response_data)
        
        print("\n" + "="*60)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"📊 Summary:")
        print(f"   - OCR Confidence: {ocr_result['confidence']}%")
        print(f"   - Keywords Extracted: {len(intelligence_result.get('keywords', []))}")
        print(f"   - Entities Found: {sum(len(v) if isinstance(v, list) else 0 for v in intelligence_result.get('entities', {}).values())}")
        print(f"   - Document Type: {intelligence_result.get('classification', {}).get('type', 'unknown')}")
        print("="*60 + "\n")
        
        return success(response_data)
        
    except ValidationError as e:
        print(f"❌ Validation Error: {str(e)}")
        return error(str(e), 400)
    except Exception as e:
        print(f"❌ Pipeline Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f"Pipeline failed: {str(e)}", 500)


@doc_pipeline_complete_bp.route('/document/intelligence', methods=['POST'])
def intelligence_only():
    """
    Document intelligence analysis only (no OCR).
    
    Request (JSON):
        {
            "text": "Document text...",
            "include_qa": true,
            "max_keywords": 10
        }
    
    Response:
        {
            "success": true,
            "data": {
                "summary": {...},
                "keywords": [...],
                "entities": {...},
                "themes": [...],
                "key_points": [...],
                "sentiment": {...},
                "qa_pairs": [...],
                "classification": {...},
                "metadata": {...}
            }
        }
    """
    try:
        data = request.json
        
        if not data or 'text' not in data:
            raise ValidationError("No text provided")
        
        text = data['text']
        include_qa = data.get('include_qa', True)
        max_keywords = data.get('max_keywords', 10)
        
        result = intelligence_service.analyze_document(
            text=text,
            include_qa=include_qa,
            max_keywords=max_keywords
        )
        
        return success(result)
        
    except ValidationError as e:
        return error(str(e), 400)
    except AIServiceError as e:
        return error(str(e), 500)


@doc_pipeline_complete_bp.route('/document/summary', methods=['POST'])
def quick_summary():
    """
    Quick summary extraction (summary + keywords only).
    
    Request (JSON):
        {
            "text": "Document text..."
        }
    
    Response:
        {
            "success": true,
            "data": {
                "summary": {...},
                "keywords": [...]
            }
        }
    """
    try:
        data = request.json
        
        if not data or 'text' not in data:
            raise ValidationError("No text provided")
        
        text = data['text']
        
        # Get full analysis but return only summary and keywords
        result = intelligence_service.analyze_document(
            text=text,
            include_qa=False,
            max_keywords=10
        )
        
        return success({
            'summary': result.get('summary', {}),
            'keywords': result.get('keywords', []),
            'sentiment': result.get('sentiment', {})
        })
        
    except ValidationError as e:
        return error(str(e), 400)
    except AIServiceError as e:
        return error(str(e), 500)
