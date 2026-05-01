import json
from flask import Blueprint, request
from services.groq_service import complete_json
from utils.response import success, error

sentiment_bp = Blueprint('sentiment', __name__)


@sentiment_bp.route('/sentiment', methods=['POST'])
def sentiment():
    """
    Analyze sentiment of provided text.
    
    Request: { "text": "..." }
    Response: { "success": true, "data": { "sentiment": "positive|negative|neutral", "positive": 0-1, "negative": 0-1, "neutral": 0-1, "explanation": "..." }, "error": null }
    """
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()

    if not text:
        return error('No text provided', 400)

    system = (
        "You are a sentiment analysis expert. Analyze the sentiment of the provided text. "
        "Return a JSON object with these exact keys: "
        "'sentiment' (one of: positive, negative, neutral), "
        "'positive' (float 0-1), 'negative' (float 0-1), 'neutral' (float 0-1), "
        "'explanation' (one sentence explaining the sentiment). "
        "The three score values must sum to 1.0. Return ONLY the JSON."
    )
    user = f"Analyze the sentiment of this text:\n\n{text}"

    try:
        raw = complete_json(system, user)
        result = json.loads(raw)
        
        sentiment_data = {
            'sentiment': result.get('sentiment', 'neutral'),
            'positive': float(result.get('positive', 0.33)),
            'negative': float(result.get('negative', 0.33)),
            'neutral': float(result.get('neutral', 0.34)),
            'explanation': result.get('explanation', ''),
        }
        
        return success(sentiment_data)
    except Exception as exc:
        return error(f"Sentiment analysis failed: {exc}", 500)
