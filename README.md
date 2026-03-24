# Damn Vulnerable AI Agent

This project is a multi-page web application built with FastAPI and HTMX. It contains 3 intentionally vulnerable AI chatbot personas for security research.

## Project Structure

```text
├── main.py              # Central FastAPI app, routing, and session management
├── llm.py               # OpenAI-compatible API client and tool-call executor
├── auth.py              # Super basic SQLite-based user authentication
├── requirements.txt     # List of static Python dependencies
├── pyproject.toml       # Modern uv project configuration
├── data/
│   └── users.db         # SQLite database for storing registered accounts
├── static/              # Raw CSS assets for our custom UI designs
│   ├── bullseye.css      # Custom design for Bullseye
│   ├── dividedhazard.css # Custom healthcare portal design
│   └── idlethat.css     # Dark-mode cloud console design
└── templates/           # Jinja2 HTML templates
    ├── base.html        # Main HTML wrapper (HTMX setup, favicons)
    ├── login.html       # Shared login and signup UI
    ├── bullseye.html    # Persona-specific page layout
    ├── ...              # Other persona layouts (dividedhazard, idlethat)
    └── partials/        # HTMX-swappable UI components
        ├── message.html # Chat message bubbles
        └── tool_call.html # Visual feedback for LLM tool execution
```

## Setup

First, configure your virtual environment and install the required packages using `uv`:

```bash
uv pip install -r requirements.txt
```

### Optional: Local LLM Backend

If you wish to host the model locally using `vLLM` (which requires a GPU), install the development dependencies:

```bash
uv sync --group dev
```

## Running the Application

To run the application locally, start the Uvicorn server:

```bash
uv run uvicorn main:app --reload --port 8080
```

> **Note:** We recommend running the FastAPI server on port `8080` in case your local LLM backend is already bound to port `8000`.

Once the server is running, you can access the three scenarios via your web browser:
- [Bullseye Scenario](http://localhost:8080/bullseye)
- [DividedHazard Scenario](http://localhost:8080/dividedhazard)
- [IDLEthat Scenario](http://localhost:8080/idlethat)

A super-basic SQLite authentication system is enabled. You will be prompted to sign up and log in for each independent persona scenario.
