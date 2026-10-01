import os
from dotenv import load_dotenv

load_dotenv()
import psycopg

conn = psycopg.connect(os.getenv("DB_URL"))
with conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS triage_runs (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW(),
            subject TEXT,
            sender TEXT,
            body TEXT,
            response TEXT,
            success BOOLEAN,
            error TEXT,
            duration_ms INTEGER
        )
    """)
print("table ready")