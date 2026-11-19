"""Workout coach that emails you: send your workout status or summary, get a motivational line and your next step.

Usage: uv run main.py "<workout summary or status>"
Every email is saved, like a couch that knows you and each new one builds on the whole history.
"""

import os
import smtplib
import sqlite3
import sys
from email.message import EmailMessage

import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

client = anthropic.Anthropic()
MODEL = "claude-haiku-5-5"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

SYSTEM = """You are a personal workout coach guiding the user through their workout plan. Keep your responses short, motivational, and actionable.
The user sends a short workout summary or status. You reply by email, very short:
one motivational phrase, then one clear next step for their next workout.
Use the history of past check-ins to track progress and keep the plan consistent.
Reply in exactly this format:
SUBJECT: <short subject>
BODY:
<motivational phrase>

Next step: <one concrete action>"""

db = sqlite3.connect("memory.db")
db.execute(
    """CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT,
        reply TEXT,
        sent_at TEXT DEFAULT CURRENT_TIMESTAMP
    )"""
)


def remember(status, reply):
    db.execute("INSERT INTO checkins (status, reply) VALUES (?, ?)", (status, reply))
    db.commit()


def recall():
    return db.execute("SELECT sent_at, status, reply FROM checkins ORDER BY id").fetchall()


def send_email(subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(EMAIL_SMTP_SERVER, 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)


def write_email(status):
    history = "\n\n".join(
        f"[{when}] I reported: {past_status}\nYou replied: {reply}"
        for when, past_status, reply in recall()
    )
    prompt = f"Past check-ins:\n{history}\n\n" if history else "This is my first check-in.\n\n"
    prompt += f"My workout status now: {status}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    subject, body = text.split("BODY:", 1)
    return subject.replace("SUBJECT:", "").strip(), body.strip()


if __name__ == "__main__":
    status = sys.argv[1]
    subject, body = write_email(status)
    print(subject, "\n\n", body)
    send_email(subject, body)
    remember(status, body)
