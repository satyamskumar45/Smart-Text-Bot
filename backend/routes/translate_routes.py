from flask import Blueprint,request,jsonify
from deep_translator import GoogleTranslator

translate_bp=Blueprint('translate',__name__)

@translate_bp.route('/translate',methods=['POST'])
def translate():
    text=request.json['text']
    target=request.json['target']
    translated=GoogleTranslator(source='auto',target=target).translate(text)
    return jsonify({'translation':translated})
