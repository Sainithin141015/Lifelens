"""
Chatbot routes – AI assistant powered by rule-based engine + optional OpenAI.
"""
import os
import json
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from services.ai_service import AIService

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/')
@login_required
def index():
    return render_template('chatbot/index.html')


@chatbot_bp.route('/ask', methods=['POST'])
@login_required
def ask():
    data = request.get_json()
    question = data.get('message', '').strip()
    if not question:
        return jsonify({'error': 'Empty message'}), 400

    try:
        response = AIService.answer(current_user, question)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Sorry, I encountered an error: {str(e)}'}), 200


@chatbot_bp.route('/weekly-summary')
@login_required
def weekly_summary():
    summary = AIService.weekly_summary(current_user)
    return jsonify({'summary': summary})
