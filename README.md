# Email Triage Agent

A small FastAPI service that reads an incoming email and decides what to do with it: create a calendar event, draft a reply, or just summarize it. Every run is logged to PostgreSQL, and the service exposes metrics on how reliably it performs.

## What it does

- `POST /triage` takes an email (subject, sender, body). An LLM agent picks one of three tools and returns the result.
- Every request is logged to Postgres: input, response, success or failure, error message, and duration in milliseconds.
- `GET /stats` returns total runs, success rate, and average duration.
- `GET /runs` returns the 10 most recent runs.
- `GET /` is a health check.

## Stack

- Python, FastAPI, Uvicorn
- LangChain agent (`create_agent`) with Groq (`openai/gpt-oss-120b`)
- PostgreSQL via `psycopg`
- Secrets loaded from `.env` with `python-dotenv`

## Sample results

From 12 test runs covering meeting requests, questions needing replies, promotional emails, a very short email, and an empty body:

| Metric | Value |
|---|---|
| Total runs | 12 |
| Successful runs | 12 |
| Success rate | 100% |
| Average duration | about 1.3 s |

This is a small manual test set, not a load test. Groq's free tier has not been tested at higher volume.
## Tool-selection eval

`eval.py` runs 9 hand-written emails through the agent and checks whether it picks the expected tool.

Result: **8/9 correct.** The one miss was a short "Thanks!" email that I labelled `summarize_only`; the agent chose `draft_reply` instead. That is a defensible choice, so the expected label for that kind of email is ambiguous.

This is a small test set written by hand, so treat it as a smoke test, not a benchmark.

## Run it locally

1. Create and activate a virtual environment, then install dependencies:
   ```
   pip install fastapi uvicorn langchain langchain-groq psycopg[binary] python-dotenv
   ```
2. Create a Postgres database named `agentlogs` with a `triage_runs` table (columns: `id`, `created_at`, `subject`, `sender`, `body`, `response`, `success`, `error`, `duration_ms`).
3. Create a `.env` file (see `.env.example`):
   ```
   GROQ_API_KEY=your_key_here
   DB_URL="host=localhost port=5432 dbname=agentlogs user=postgres password=your_password"
   ```
4. Start the server:
   ```
   uvicorn main:app --reload
   ```
5. Open `http://127.0.0.1:8000/docs` and try `POST /triage`.

Example request:
```json
{
  "subject": "Meeting Thursday",
  "sender": "temesgen@example.com",
  "body": "Can we meet Thursday at 3pm to go over the refund?"
}
```

## Known limitations

- `draft_reply` creates real Gmail drafts through the Gmail API (it never sends email). `create_calendar_event` and `summarize_only` are still stubs; connecting calendar events to the Google Calendar API is the next step. Draft wording is not tuned yet (it can leave placeholders such as the sender name).
- No authentication on the endpoints.
- Runs locally only; not deployed. Optional: to create real Gmail drafts, enable the Gmail API in Google Cloud, download an OAuth desktop client as `credentials.json` into the project folder, and set `USE_REAL_GMAIL=1` in `.env`. The first run opens a browser to sign in.

## Related work

The same triage idea was first built as an n8n workflow (Gmail trigger, AI agent, calendar and draft tools). This repo is the code-based version with logging and metrics.
