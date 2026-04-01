# Slim FastAPI image for Google Cloud Run (API dependencies only).
# Build from repo root: docker build -f tippelaget-web/api/Dockerfile tippelaget-web/api
# Or: gcloud run deploy --source ./tippelaget-web/api (uses this Dockerfile)

FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    REPO_ROOT=/app

WORKDIR /app

# Wheels only for linux/amd64; add build deps only if a future dependency needs compilation.
RUN pip install --no-cache-dir \
    "fastapi>=0.115,<1" \
    "uvicorn[standard]>=0.32,<1" \
    "python-dotenv>=1,<2" \
    "pydantic-settings>=2.6,<3" \
    "pandas>=2.3.1,<3" \
    "cognite-sdk>=7.80.2,<8" \
    "openai>=1.100.1,<2"

COPY . /app

# Cloud Run sets PORT; listen on all interfaces.
CMD exec uvicorn main:app --host 0.0.0.0 --port "${PORT}"
