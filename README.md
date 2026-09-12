# DataHealth

A data quality workspace for profiling, validating, and cleaning CSV datasets. Built with Next.js, React, FastAPI, pandas, and SQLite.

## Features

- Upload a CSV up to 20 MB and follow background analysis.
- Explore column types, missing values, unique values, and numeric statistics.
- Review completeness, validity, consistency, and uniqueness scores.
- Inspect duplicate records, formatting problems, and other quality issues.
- Trim whitespace, normalize casing, and remove duplicates.
- Refresh profiles and scores after cleaning, then export the resulting CSV.
- Browse and search dataset history in a responsive dashboard.

## Requirements

- Node.js 20.9 or later and npm
- Python 3.11 or later (tested with Python 3.13)

## Quick start

Clone the repository and open two terminals in its root directory.

### 1. Start the API

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

On macOS/Linux, use `.venv/bin/python` instead of `.venv\Scripts\python.exe`.

Run the backend from the repository root: its database, upload paths, and sample dataset use relative paths. SQLite tables and upload directories are created automatically.

### 2. Start the frontend

```powershell
cd frontend
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Select **Explore a sample dataset** or upload your own CSV. Interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

The included sample uses fictional records and reserved `example.com` email addresses, with intentional quality problems.

## Configuration

The frontend forwards `/api/*` requests to `http://127.0.0.1:8000`. To change this, set the server-side `API_URL` environment variable before starting or building Next.js. Browser requests remain on the same origin.

```powershell
$env:API_URL = "http://127.0.0.1:8000"
npm run dev
```

## Checks and production build

From `frontend/`:

```powershell
npm run lint
npm run build
npm run start
```

The API must remain running alongside the frontend. A frontend build alone does not host the Python backend. Persist the SQLite database and `uploads/` directory if deploying beyond local development.

## Project structure

```text
backend/
  api/          Upload, job, and cleaning endpoints
  profiling/    Column statistics and semantic type inference
  validators/   Quality checks
  services/     Background processing and scoring
  database.py   SQLite models and sessions
  main.py       FastAPI application
frontend/
  src/app/      Dashboard, dataset views, and shared styles
  public/       Static assets
sample-data/    Synthetic example CSV
```

## Data handling and limitations

Original CSV uploads are retained; cleaning writes a separate file. Local databases, uploaded datasets, virtual environments, and build output are excluded from Git.

This is a local, single-workspace application without authentication or tenant isolation. Add those controls before exposing it to untrusted users. Validation is heuristic: review findings and casing changes before using exported data. Issue occurrences can overlap within a record and are not a count of distinct affected rows.

The health score weights completeness (25%), validity (30%), consistency (20%), and uniqueness (15%), plus a fixed 10-point baseline. It is a quality indicator, not a guarantee of correctness.

## Deploy to Railway

The root Dockerfile packages Next.js and FastAPI into one service. Railway builds it directly from this repository. The API listens only inside the container, and Next.js forwards browser API requests to it.

1. In [Railway](https://railway.com/new), choose **Deploy from GitHub repo** and select `Eshgin10/DataHealth`.
2. Use the repository root as the service root. Railway detects `Dockerfile` and `railway.toml` automatically.
3. Attach a persistent volume at `/data` **before uploading real datasets**. The SQLite database and raw/cleaned uploads live there. Without a volume, redeployments lose that data.
4. Set `PORT=3000`. Leave `API_URL` unset: the image builds with the internal API address. Keep a single replica because the app uses SQLite and local files.
5. Under Networking, generate a public domain with target port `3000`.
6. Wait for a healthy deployment. Open the domain, run the sample dataset, apply a cleaning action, and download the result. `/api/health` should return `{"status":"ok"}`.

Review Railway's displayed plan and storage charges before accepting paid resources. No hosting subscription is provisioned by these repository files.

**Audience:** the app currently has a shared dataset list and no login. Use synthetic/non-sensitive data for a public demo. Add authentication and per-user data isolation before accepting private datasets.

The container startup script waits for the API, starts Next.js, forwards termination signals, and exits if either service fails so the platform can restart it. The health check reaches the API through the frontend.

### Build and run with Docker

```sh
docker build -t datahealth .
docker run --rm -p 3000:3000 -v datahealth-data:/data datahealth
```

Container execution must be verified on a machine with Docker or by Railway's build. Local Python/TypeScript checks do not replace a container build.
