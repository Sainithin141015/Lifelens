# LifeLens AI – Personal Analytics & Future Outcome Prediction System

A full-stack hackathon application that combines financial analytics, study intelligence, habit tracking, ML predictions, and an AI chatbot.

## Features

- 🔐 **Authentication** – Register, Login, Profile management
- 💰 **Financial Analytics** – Income/expense tracking, savings forecast, ML predictions
- 📚 **Study Intelligence** – Session logging, subject analysis, CGPA prediction
- 💪 **Habit Analytics** – Daily habit logging, lifestyle score, pattern analysis
- 🔮 **Simulation Engine** – What-if scenarios for finance, study, and lifestyle
- 🤖 **AI Chatbot** – Personalized insights from your actual data
- 🏆 **Achievement Badges** – Gamified progress tracking
- 🌙 **Dark Mode** – Toggle-able dark theme

## Quick Start

```bash
# 1. Install dependencies
pip install flask flask-sqlalchemy flask-login flask-wtf werkzeug psycopg2-binary \
            pandas numpy scikit-learn joblib python-dotenv wtforms email-validator \
            requests reportlab openai

# 2. Set DATABASE_URL (or uses SQLite as fallback)
export DATABASE_URL=postgresql://user:pass@localhost/lifelens

# 3. Run
cd lifelens
python app.py

# 4. Access in browser
open http://localhost:5000
```

## Demo Account
- Email: `demo@lifelens.ai`
- Password: `demo1234`

## Tech Stack
- **Backend**: Python, Flask, SQLAlchemy, Flask-Login
- **Database**: PostgreSQL (SQLite fallback)
- **ML**: Scikit-learn, NumPy, Pandas
- **Frontend**: HTML5, Bootstrap 5, Chart.js
- **AI**: Rule-based engine + optional OpenAI API
# Lifelens
