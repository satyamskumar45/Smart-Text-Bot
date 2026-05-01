
from flask import Blueprint,request,jsonify

chatbot_bp=Blueprint('chatbot',__name__)

@chatbot_bp.route('/chat',methods=['POST'])
def chat():
    msg=request.json['message']
    response=f"You said: {msg}"
    return jsonify({'reply':response})
=======
import json
from flask import Blueprint, request, g
from services.groq_service import complete_json
from services.history_service import save_history_entry
from services.auth_service import track_guest_usage
from middleware.auth_middleware import optional_auth
from utils.response import success, error

chatbot_bp = Blueprint('chatbot', __name__)

SYSTEM_PROMPT = (
    "You are SmartTextBot, an intelligent AI language assistant. "
    "You help users with translation, text analysis, writing improvement, and language questions. "
    "Be helpful, concise, and friendly."
)


@chatbot_bp.route('/chat', methods=['POST'])
@optional_auth
def chat():
    """
    Chat with the AI assistant.
    
    Request: { "message": "...", "history": [...] }
    Response: { "success": true, "data": { "reply": "..." }, "error": null }
    """
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()
    history = data.get('history', [])

    if not message:
        return error('No message provided', 400)

    # Build message history for Groq API
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for h in history[-10:]:
        if h.get('role') in ('user', 'assistant') and h.get('content'):
            messages.append({"role": h['role'], "content": h['content']})
    
    messages.append({"role": "user", "content": message})

    try:
        from services.groq_service import complete
        reply = complete(SYSTEM_PROMPT, message, model="llama-3.1-8b-instant")

        current = getattr(g, 'current_user', None)
        if current:
            save_history_entry(
                user_id=current.get('id') if current.get('role') == 'user' else None,
                guest_session_id=current.get('guest_session_id') if current.get('role') == 'guest' else None,
                module_type='language_quest',
                input_text=message,
                output_text=reply,
                metadata=json.dumps({'history_length': len(history)}),
            )
            if current.get('role') == 'guest':
                track_guest_usage(current.get('guest_session_id'), 'language_quest')

        print(f"[CHAT] Processed message, reply length: {len(reply)} chars")
        return success({'reply': reply})

    except Exception as e:
        print(f"[ERROR] Chat failed: {str(e)}")
        return error(f"Chat failed: {str(e)}", 500)
