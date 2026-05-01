from flask import Blueprint,request,send_file
from gtts import gTTS
import uuid

voice_bp=Blueprint('voice',__name__)

@voice_bp.route('/tts',methods=['POST'])
def tts():
    text=request.json['text']
    filename=f"speech_{uuid.uuid4()}.mp3"
    tts=gTTS(text)
    tts.save(filename)
    return send_file(filename)
