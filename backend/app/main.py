from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List, Optional
import openai
import os
from datetime import datetime
import json
import io

# Optional dependencies for PDF and spreadsheet handling
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pandas as pd
except ImportError:
    pd = None

app = FastAPI()

# CORS configuration to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Load OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Database configuration using SQLite for simplicity
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


class Client(SQLModel, table=True):
    """Represents a client entity."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str


class Task(SQLModel, table=True):
    """Represents a task assigned to a client or internal work item."""
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    status: str
    client_id: Optional[int] = Field(default=None, foreign_key="client.id")


class Appointment(SQLModel, table=True):
    """Represents an appointment between a client and the CA."""
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: Optional[int] = Field(default=None, foreign_key="client.id")
    scheduled_time: datetime
    description: str


@app.on_event("startup")
def on_startup() -> None:
    """Initialise the SQLite database and create tables on startup."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Dependency to provide a SQLModel session."""
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root() -> dict:
    """Root endpoint for health check."""
    return {"message": "Welcome to CA Suite"}


# ----- Clients API -----

@app.get("/clients")
def list_clients(session: Session = Depends(get_session)) -> List[Client]:
    """Return a list of all clients."""
    return session.exec(select(Client)).all()


@app.post("/clients")
def create_client(client: Client, session: Session = Depends(get_session)) -> Client:
    """Create a new client."""
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


# ----- Tasks API -----

@app.get("/tasks")
def list_tasks(session: Session = Depends(get_session)) -> List[Task]:
    """Return a list of all tasks."""
    return session.exec(select(Task)).all()


@app.post("/tasks")
def create_task(task: Task, session: Session = Depends(get_session)) -> Task:
    """Create a new task."""
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# ----- Appointments API -----

@app.get("/appointments")
def list_appointments(session: Session = Depends(get_session)) -> List[Appointment]:
    """Return a list of all appointments."""
    return session.exec(select(Appointment)).all()


@app.post("/appointments")
def create_appointment(appointment: Appointment, session: Session = Depends(get_session)) -> Appointment:
    """Create a new appointment."""
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


# ----- AI Generation API -----

from pydantic import BaseModel


class Prompt(BaseModel):
    """Schema for the AI prompt input."""
    prompt: str


@app.post("/generate_reply")
def generate_reply(prompt: Prompt) -> dict:
    """
    Generate an AI-powered reply for a given prompt using OpenAI's ChatGPT API.

    Raises a 500 error if the API key is not configured.
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You draft professional replies for CAs dealing with tax notices."},
            {"role": "user", "content": prompt.prompt},
        ],
        max_tokens=512,
        temperature=0.2,
    )
    reply_text = completion.choices[0].message.content
    return {"reply": reply_text}


# ----- GST Notice Analysis -----

@app.post("/gst_notice")
async def gst_notice(
    notice: UploadFile = File(...), additional_docs: List[UploadFile] | None = File(None)
) -> dict:
    """
    Analyse an uploaded GST notice. Extract text from the notice, determine missing
    documents based on simple heuristics, and use the OpenAI API to draft a reply
    when appropriate.
    """
    content = await notice.read()
    text: str = ""
    # Extract text from PDF if pdfplumber is installed
    if pdfplumber:
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception:
            # Fallback to raw decode if PDF parsing fails
            text = content.decode("utf-8", errors="ignore")
    else:
        # If pdfplumber not available, decode bytes directly
        text = content.decode("utf-8", errors="ignore")

    # Simple heuristic to identify missing documents
    missing_docs: List[str] = []
    if "late fee" in text.lower():
        missing_docs.append("Proof of late fee payment")

    reply: str = ""
    if not missing_docs and OPENAI_API_KEY:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You draft formal replies to GST notices based on provided notices."},
                {"role": "user", "content": text},
            ],
            max_tokens=512,
            temperature=0.2,
        )
        reply = completion.choices[0].message.content
    return {"reply": reply, "missing_documents": missing_docs}


# ----- Tally Data Import -----

@app.post("/import_tally")
async def import_tally(file: UploadFile = File(...)) -> dict:
    """
    Accept a CSV or JSON export from Tally, parse it using pandas, and return a
    summary of numeric columns. Requires pandas to be installed.
    """
    content = await file.read()
    if not pd:
        raise HTTPException(status_code=500, detail="pandas is required for this endpoint")
    df = None
    # Determine file type based on extension
    filename = file.filename.lower()
    if filename.endswith(".json"):
        try:
            data_json = json.loads(content.decode())
            df = pd.json_normalize(data_json)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
    else:
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid CSV file")
    totals: dict = {}
    if df is not None:
        numeric_cols = df.select_dtypes(include="number").columns
        for col in numeric_cols:
            totals[col] = float(df[col].sum())
    return {"rows": len(df) if df is not None else 0, "totals": totals}
