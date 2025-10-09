# syntax=docker/dockerfile:1.7
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# non-root User
RUN useradd -m appuser
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app/
RUN chown -R appuser:appuser /app
USER appuser

# Prod-Start (keine Access-Logs, kein Reload)
CMD ["sh","-c","alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log"]
