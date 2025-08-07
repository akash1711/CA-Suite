"""
FastAPI application for the CA‑Suite backend.

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

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from typing import List, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

# Additional libraries for file processing.  These imports are optional
# and only used in the GST notice analysis and Tally import endpoints.
try:
    import pdfplumber  # type: ignore[import]
except ImportError:
    pdfplumber = None
try:
    import pandas as pd  # type: ignore[import]
except ImportError:
    pd = None

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


# ----------------------------------------------------------------------------
# Database models and configuration
#
# We use SQLModel to define lightweight ORM models for clients, tasks and
# appointments.  A simple SQLite database is used by default; the location
# can be overridden by setting the DATABASE_URL environment variable.  When
# the application starts up it will automatically create tables if they do
# not already exist.  Each model inherits from SQLModel to provide both
# ORM functionality and Pydantic validation for request/response bodies.

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ca_suite.db")

engine = create_engine(DATABASE_URL, echo=False)


class Client(SQLModel, table=True):  # type: ignore[call-arg]
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None


class Task(SQLModel, table=True):  # type: ignore[call-arg]
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    status: str = "pending"
    client_id: Optional[int] = Field(default=None, foreign_key="client.id")


class Appointment(SQLModel, table=True):  # type: ignore[call-arg]
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    scheduled_time: str  # store ISO datetime strings for simplicity
    description: Optional[str] = None


def get_session():
    """
    FastAPI dependency that yields a SQLModel session.  A new session is
    created for each request and closed when the request is complete.
    """
    with Session(engine) as session:
        yield session


app = FastAPI(title="CA‑Suite Backend", version="0.1.0")

# Configure CORS so that the frontend (which may be served from a different
# origin during development) can communicate with this API.  In production
# you should replace "*" with the actual allowed origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup.  This ensures that the SQLite
# database is initialised before any requests are processed.  If the
# tables already exist, this call is a no‑op.
@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)


@app.get("/")
async def read_root():
    """Return a simple welcome message."""
    return {"message": "Welcome to the CA‑Suite backend API"}


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
    # Always return the generated text under the key "reply" so that the
    # frontend can access the generated text predictably.
    return {"reply": choice}


# ---------------------------------------------------------------------------
# CRUD endpoints for Clients
#
# These endpoints allow creating and retrieving client records.  The POST
# endpoint accepts a JSON body containing at least a `name` and optionally
# an `email`.  The GET endpoint returns all clients in the database.

@app.get("/clients", response_model=List[Client])
def get_clients(*, session: Session = Depends(get_session)) -> List[Client]:
    """Retrieve all clients from the database."""
    statement = select(Client)
    clients = session.exec(statement).all()
    return clients


@app.post("/clients", response_model=Client)
def create_client(client: Client, *, session: Session = Depends(get_session)) -> Client:
    """Create a new client record in the database."""
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


# ---------------------------------------------------------------------------
# CRUD endpoints for Tasks
#
# Tasks can optionally be associated with a client via `client_id`.  The
# `status` field defaults to "pending" but can be updated when required.

@app.get("/tasks", response_model=List[Task])
def get_tasks(*, session: Session = Depends(get_session)) -> List[Task]:
    """Retrieve all tasks from the database."""
    statement = select(Task)
    tasks = session.exec(statement).all()
    return tasks


@app.post("/tasks", response_model=Task)
def create_task(task: Task, *, session: Session = Depends(get_session)) -> Task:
    """Create a new task record in the database."""
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# ---------------------------------------------------------------------------
# CRUD endpoints for Appointments
#
# Appointments require an associated client via `client_id` and a
# `scheduled_time`.  Times are stored as ISO formatted strings for
# simplicity and can be parsed by the frontend.

@app.get("/appointments", response_model=List[Appointment])
def get_appointments(*, session: Session = Depends(get_session)) -> List[Appointment]:
    """Retrieve all appointments from the database."""
    statement = select(Appointment)
    appointments = session.exec(statement).all()
    return appointments


@app.post("/appointments", response_model=Appointment)
def create_appointment(
    appointment: Appointment, *, session: Session = Depends(get_session)
) -> Appointment:
    """Create a new appointment record in the database."""
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment

# ---------------------------------------------------------------------------
# GST notice analysis and reply endpoint
#
# This endpoint accepts a GST/IT notice as an uploaded file (PDF or text)
# along with any additional supporting documents.  It extracts text from
# the notice, determines whether additional documents are required (based
# on simple heuristics), and drafts a formal reply using the OpenAI
# Chat API when possible.

@app.post("/gst_notice")
async def gst_notice(
    notice: UploadFile = File(...),
    additional_documents: List[UploadFile] | None = File(None),
):
    """
    Analyse a GST/IT notice and optionally draft a reply.

    Returns a draft reply and a list of missing documents if any.
    """
    content = await notice.read()
    text = ""
    # Extract text from PDF if possible
    if pdfplumber is not None and notice.filename.lower().endswith(".pdf"):
        try:
            import io
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text() or ""
                    text += extracted
        except Exception:
            text = ""
    # Fallback to treating the content as plain text
    if not text:
        try:
            text = content.decode("utf-8", errors="ignore")
        except Exception:
            text = ""
    missing: List[str] = []
    lower = text.lower()
    if "late fee" in lower or "penalty" in lower:
        missing.append("Proof of payment for late fee/penalty")
    if "invoice" in lower and (not additional_documents or len(additional_documents) == 0):
        missing.append("Supporting invoices")
    if missing:
        return {"reply": "", "missing_documents": missing}
    reply = ""
    if OPENAI_API_KEY:
        try:
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant drafting formal replies to GST notices."},
                    {"role": "user", "content": f"Draft a professional response to the following notice:\n{text}"},
                ],
                max_tokens=512,
                temperature=0.2,
            )
            reply = completion.choices[0].message.content
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))
    return {"reply": reply, "missing_documents": missing}


# ---------------------------------------------------------------------------
# Tally data import endpoint
#
# Accepts a CSV or JSON file exported from Tally and returns sums of numeric
# columns as a simple financial summary.

@app.post("/import_tally")
async def import_tally(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename.lower()
    if pd is None:
        raise HTTPException(status_code=500, detail="pandas library is not installed on the server")
    import io, json
    try:
        if filename.endswith(".json"):
            json_obj = json.loads(content.decode())
            data = pd.json_normalize(json_obj)
        else:
            data = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid file format: {exc}")
    totals = {}
    for col in data.columns:
        if pd.api.types.is_numeric_dtype(data[col]):
            totals[col] = float(data[col].sum())
    return {"totals": totals, "row_count": int(len(data))}
