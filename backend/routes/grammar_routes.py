from flask import Blueprint,request,jsonify
import language_tool_python

grammar_bp=Blueprint('grammar',__name__)
tool=language_tool_python.LanguageTool('en-US')

@grammar_bp.route('/grammar',methods=['POST'])
def grammar():
    text=request.json['text']
    matches=tool.check(text)
    corrected=language_tool_python.utils.correct(text,matches)
    return jsonify({'corrected':corrected})
