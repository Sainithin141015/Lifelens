# LifeLens AI Tests

This folder contains automated pytest tests for the LifeLens AI Flask application.

## Run the tests

From the `lifelens` folder:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests/ -v
```

The tests use an isolated in-memory SQLite database and disable external AI keys, so they do not modify the normal application database or call Gemini/OpenAI.

## Test count

The suite currently contains 16 tests covering application startup, authentication, finance, study, habits, simulation, and chatbot validation.
