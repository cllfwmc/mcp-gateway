# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --wheel-dir=/wheels -r requirements.txt

FROM base AS runtime
ENV PORT=8000
WORKDIR /app
COPY --from=builder /wheels /wheels
COPY --from=builder /usr/local/bin /usr/local/bin
RUN pip install --no-index --find-links=/wheels -r /wheels/requirements.txt || pip install --no-index --find-links=/wheels fastapi uvicorn[standard] httpx pydantic python-multipart jinja2 itsdangerous starlette orjson
COPY backend ./backend
COPY ui ./ui
COPY configs ./configs
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
