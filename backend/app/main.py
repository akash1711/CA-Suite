"""
FastAPI application for the CA Suite backend.

This module defines a simple API that exposes endpoints for
health checks and for generating AI‑powered responses.  It uses
OpenAI's API via the `openai` python client.  The OpenAI API
key should be provided via an environment variable called
`OPENAI_API_KEY`.  For development you can create a `.env`
file at the project root and set your key there (see
python‑dotenv for loading environment variables from files).

The `/` root endpoint returns a welcome message to verify that
the service is up.  The `/generate_reply` endpoint accepts a
JSON payload with a `prompt` field and returns the model’s
response.  You can extend this pattern to implement features
such as notice parsing, document summarisation or draft
generation for GST/IT replies.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os

# Load environment variables if a .env file is present.  This
# call is safe even if python‑dotenv isn't installed (it will
# simply do nothing).  The import is optional but helps when
# running locally.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv is an optional dependency for loading env files.
    pass


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


class Prompt(BaseModel):
    """Pydantic model representing a user prompt for AI generation."""

    prompt: str


app = FastAPI(title="CA Suite Backend", version="0.1.0")


@app.get("/")
async def read_root():
    """Return a simple welcome message."""
    return {"message": "Welcome to the CA Suite backend API"}


@app.post("/generate_reply")
async def generate_reply(data: Prompt):
    """Generate a text response using OpenAI's GPT model.

    Args:
        data: JSON body with a single field `prompt` containing
            the user input text.

    Returns:
        A dictionary containing the generated response.
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    # Compose a simple chat completion request.  For more advanced
    # behaviour (system messages, function calling, etc.), extend
    # this request accordingly.
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": data.prompt}],
            max_tokens=512,
            temperature=0.2,
        )
    except Exception as exc:
        # Catch network or API errors and surface them to the client.
        raise HTTPException(status_code=500, detail=str(exc))

    # Extract the first choice text from the response.
    choice = completion.choices[0].message.content if completion.choices else ""
    return {"response": choice}
