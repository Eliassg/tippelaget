# Tippelaget web (React + FastAPI)

React + FastAPI app in this folder. Local Python deps use the repository root **`pyproject.toml`** optional extra **`web`**.

**Production layout (intended):**

| Piece | Where | Notes |
|--------|--------|--------|
| Frontend | **GitHub Pages** | Static Vite build; workflow `.github/workflows/deploy-pages.yml` |
| Backend | **Google Cloud Run** | `tippelaget-web/api/Dockerfile`; scales to zero |

## Prerequisites

- Node.js 20+ and npm
- Python 3.10+ (local API dev)
- [Poetry](https://python-poetry.org/) (recommended) for `poetry install --extras web`
- For production: Google Cloud project with **Cloud Run** and **Artifact Registry** (or use **Cloud Run deploy from source**, which uses Cloud Build)

## Configuration (API)

1. Copy `api/env.example` to `api/.env` for local runs.
2. Required variables for Cognite + OpenAI (same names you use elsewhere for this project):

- `COGNITE_PROJECT`, `COGNITE_BASE_URL`, `COGNITE_CLIENT_ID`, `COGNITE_CLIENT_SECRET`, `COGNITE_TOKEN_URL`
- `OPENAI_API_KEY`

3. **GitHub Pages + Cloud Run:** set **`CORS_EXTRA_ORIGINS`** on the Cloud Run service to your Pages origin, e.g. `https://youruser.github.io` (scheme + host only, no `/repo` path).

Optional: **`REPO_ROOT`** — in the Docker image defaults to `/app`; add player PNGs into the image or mount storage if you use `/api/player-image/{name}`.

## Deploy the API (Google Cloud Run)

From the **repository root**, with `gcloud` logged in and a project selected:

```bash
gcloud run deploy tippelaget-api \
  --source ./tippelaget-web/api \
  --region europe-north1 \
  --allow-unauthenticated \
  --min-instances=0 \
  --set-env-vars="COGNITE_PROJECT=...,COGNITE_BASE_URL=...,COGNITE_CLIENT_ID=...,COGNITE_CLIENT_SECRET=...,COGNITE_TOKEN_URL=...,OPENAI_API_KEY=...,CORS_EXTRA_ORIGINS=https://YOURUSER.github.io"
```

Prefer **Secret Manager** for `OPENAI_API_KEY` / `COGNITE_CLIENT_SECRET` instead of inline env vars in a public repo workflow; see [Cloud Run secrets](https://cloud.google.com/run/docs/configuring/secrets).

After deploy, note the **service URL** (e.g. `https://tippelaget-api-….run.app`).

**Local Docker check:**

```bash
docker build -t tippelaget-api -f tippelaget-web/api/Dockerfile tippelaget-web/api
docker run --rm -p 8080:8080 \
  --env-file tippelaget-web/api/.env \
  -e PORT=8080 \
  tippelaget-api
```

## Deploy the UI (GitHub Pages)

1. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. **Settings → Secrets and variables → Actions**
   - **Secret `VITE_API_BASE_URL`** = your Cloud Run URL, **no trailing slash** (same value you use in the browser).
3. Push to `main` or run workflow **Deploy GitHub Pages** manually.

The workflow sets **`VITE_BASE_PATH`** to `/repo-name/` for project pages, or `/` for a `username.github.io` repository. Override with repository **variable `VITE_BASE_PATH`** if needed (custom domain, etc.).

It copies **`404.html`** from `index.html` so deep links work on refresh.

## Run locally (two terminals)

**API (Poetry):**

```bash
cd /path/to/tippelaget
poetry install --extras web
cd tippelaget-web/api
poetry run uvicorn main:app --reload --port 8000
```

**Frontend:**

```bash
cd tippelaget-web/frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173); Vite proxies `/api` to port 8000.

### `requirements.txt` for other tooling

```bash
cd /path/to/tippelaget
poetry export -f requirements.txt --without-hashes --extras web -o tippelaget-web/api/requirements.txt
```

## Features

- Eight metric views, Prophet + King assistants, today’s events, workflow populate + last run
