# SupportPilot

SupportPilot is an AI-powered customer support automation project built with Python, FastAPI, Streamlit, LangGraph, Groq, and ChromaDB.

## Features

- Retrieve answers from a support knowledge base using semantic search.
- Answer customer questions about shipping, returns, refunds, warranties, and troubleshooting.
- Look up demo order information.
- Create support tickets with explicit user confirmation.
- Evaluate retrieval and answer behavior with automated tests.

## Tech Stack

- Python
- FastAPI
- Streamlit
- LangGraph
- Groq API
- ChromaDB
- Sentence Transformers
- SQLite
- Pytest

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   `pip install -r requirements.txt`

3. Copy `.env.example` to `.env` and add your own Groq API key.
4. Initialize the demo database using the project's database initialization script.
5. Start the Streamlit application:

   `streamlit run app.py`

## Tests

Run the test suite from the project root:

`python -m pytest -v`

## Project Status

This is a portfolio and learning project using synthetic demo data. It is not a production-ready customer support service. Authentication, production data security, and additional evaluation are future improvements.
