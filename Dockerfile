# syntax=docker/dockerfile:1

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# System deps (curl for health/debug, no extra packages required now)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure DB directory exists (DB path is src/db/database.db)
RUN mkdir -p /app/src/db

# Env var for token; set at runtime: -e BOT_TOKEN=...
ENV BOT_TOKEN=""

CMD ["python", "main.py"]
