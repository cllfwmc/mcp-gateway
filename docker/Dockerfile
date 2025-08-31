FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=on

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# App code
COPY gateway /app/gateway
COPY config.json /app/config.json

EXPOSE 8000

CMD ["uvicorn", "gateway.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
