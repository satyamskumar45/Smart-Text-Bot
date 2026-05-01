from flask import Blueprint,request,jsonify

chatbot_bp=Blueprint('chatbot',__name__)

@chatbot_bp.route('/chat',methods=['POST'])
def chat():
    msg=request.json['message']
    response=f"You said: {msg}"
    return jsonify({'reply':response})
