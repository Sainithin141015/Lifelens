"""
LifeLens AI – Configuration
"""

import os


class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'lifelens-dev-secret-key-2024')

    # PostgreSQL via DATABASE_URL (Replit-managed)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///lifelens.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # OpenAI (optional – chatbot falls back gracefully if not set)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.environ.get('AI_INTEGRATIONS_OPENAI_BASE_URL', 'https://api.openai.com/v1')

    # Gemini (preferred – used when GEMINI_API_KEY is set)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

    # Upload / model storage
    MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_models', 'saved')
    os.makedirs(MODEL_DIR, exist_ok=True)

    # WTForms CSRF
    WTF_CSRF_ENABLED = True
