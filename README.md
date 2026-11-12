# email-memory-agent

A workout coach powered by Claude Haiku 5.5. Send it your workout summary or status. It emails you back a short motivational phrase and your next step. Every check-in is stored in SQLite, so each reply builds on your whole history.

## Setup

1. Fill in `.env`: `ANTHROPIC_API_KEY`, `EMAIL_ADDRESS`, `EMAIL_SMTP_SERVER`, `EMAIL_APP_PASSWORD` (Gmail app password: https://myaccount.google.com/apppasswords)
2. `uv sync`

## Usage

```
uv run main.py "Chest and triceps, 45 min, felt strong."
uv run main.py "Skipped legs, sore knee."
```

Memory lives in `memory.db` (gitignored).
