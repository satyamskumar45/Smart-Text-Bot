from flask import Blueprint, request, current_app
from services.chatbot_service import analyze_sentiment
from utils.response import success, error

sentiment_bp = Blueprint('sentiment', __name__)


@sentiment_bp.route('/sentiment', methods=['POST'])
def sentiment():
    """
    Analyze sentiment of provided text.

    Request: { "text": "..." }
    Response: {
        "success": true,
        "data": {
            "sentiment": "positive|negative|neutral",
            "positive": 0-1,
            "negative": 0-1,
            "neutral": 0-1,
            "explanation": "..."
        }
    }
    """

    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()

    if not text:
        return error('No text provided', 400)

    try:
        sentiment_data = analyze_sentiment(text)
        return success(sentiment_data)

    except ValueError as ve:
        current_app.logger.info("Sentiment validation error: %s", ve)
        return error(str(ve), 400)

    except Exception as exc:
        current_app.logger.exception("Sentiment analysis failed")
        return error(f"Sentiment analysis failed: {exc}", 500)