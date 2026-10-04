import time
import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain_core.tools import tool
from gmail_tools import create_gmail_draft
load_dotenv()

DB_URL = os.getenv("DB_URL")
USE_REAL_GMAIL = os.getenv("USE_REAL_GMAIL") == "1"
@tool
def create_calendar_event(title: str, date: str, time: str) -> str:
    """Create a calendar event for a meeting. Use when the email is requesting a meeting."""
    return f"Event created: '{title}' on {date} at {time}"

@tool
def draft_reply(to: str, subject: str, body: str) -> str:
    """Draft an email reply. Use when the email needs a response."""
    if USE_REAL_GMAIL:
        draft_id = create_gmail_draft(to, subject, body)
        return f"Gmail draft created (id {draft_id}) to {to} - Subject: {subject}"
    return f"Draft created to {to} - Subject: {subject}"

@tool
def summarize_only(summary: str) -> str:
    """Use when no action is needed, just summarize the email."""
    return f"Summary: {summary}"

agent = create_agent(
    model="groq:openai/gpt-oss-120b",
    tools=[create_calendar_event, draft_reply, summarize_only],
    system_prompt="""You are an email triage assistant. Given an email's subject and body,
    decide the appropriate action: if it's a meeting request, create a calendar event;
    if it needs a reply, draft a response; otherwise summarize it.
    Always use one of the tools available - never respond with plain text only."""
)

app = FastAPI()

class Email(BaseModel):
    subject: str
    sender: str
    body: str

def log_run(email, response, success, error, duration_ms):
    with psycopg.connect(DB_URL) as conn:
        conn.execute(
            "INSERT INTO triage_runs (subject, sender, body, response, success, error, duration_ms) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (email.subject, email.sender, email.body, response, success, error, duration_ms),
        )

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/triage")
def triage(email: Email):
    text = f"Subject: {email.subject}\nFrom: {email.sender}\nBody: {email.body}"
    start = time.time()
    try:
        result = agent.invoke({"messages": [{"role": "user", "content": text}]})
        response = result["messages"][-1].content
        log_run(email, response, True, None, int((time.time() - start) * 1000))
        return {"response": response}
    except Exception as e:
        log_run(email, None, False, str(e), int((time.time() - start) * 1000))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def stats():
    with psycopg.connect(DB_URL) as conn:
        total, ok, avg = conn.execute(
            "SELECT COUNT(*), COUNT(*) FILTER (WHERE success), COALESCE(AVG(duration_ms), 0) FROM triage_runs"
        ).fetchone()
    return {
        "total_runs": total,
        "successful_runs": ok,
        "success_rate_pct": round(100 * ok / total, 1) if total else None,
        "avg_duration_ms": round(float(avg)),
    }

@app.get("/runs")
def runs():
    with psycopg.connect(DB_URL) as conn:
        rows = conn.execute(
            "SELECT id, created_at, subject, success, duration_ms FROM triage_runs ORDER BY id DESC LIMIT 10"
        ).fetchall()
    return [
        {"id": r[0], "created_at": r[1].isoformat(), "subject": r[2], "success": r[3], "duration_ms": r[4]}
        for r in rows
    ]