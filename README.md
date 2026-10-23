# Northstar — Collaborative Project Management

A local-first hackathon starter for the NeoStats Collaborative Project Management Platform brief.

## Stack
- Frontend: Next.js App Router, React, TypeScript, Tailwind CSS
- Backend: Python 3.11+, FastAPI, SQLAlchemy, JWT
- Database: local MySQL

## Important
This is a hackathon starter, not a production-hardened system. Review and test authorization, authentication, and concurrency behavior before presenting it. Never commit real secrets.

## Prerequisites
- Node.js 22+
- Python 3.11+
- MySQL Server running locally
- Git

## 1. Create the MySQL database
Log in to MySQL using your local MySQL client and run:

```sql
CREATE DATABASE neostats_pm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2. Start the backend
Open a terminal in `backend`:

Windows PowerShell:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `backend/.env` with your local MySQL username/password and a long random `JWT_SECRET`.

```powershell
python -m app.seed
uvicorn app.main:app --reload --port 8000
```
API docs: http://127.0.0.1:8000/docs

Seeded demo accounts (change passwords before any real use):
- admin@northstar.local / Demo123!
- manager@northstar.local / Demo123!
- member@northstar.local / Demo123!
- viewer@northstar.local / Demo123!

## 3. Start the frontend
Open another terminal in `frontend`:

```powershell
npm install
Copy-Item .env.example .env.local
npm run dev
```
Open http://localhost:3000.

If login cannot reach the API, make sure MySQL is running, the database and `backend/.env` are configured, and the backend is running on port 8000. Verify it at http://127.0.0.1:8000/api/health before signing in. The frontend calls the backend directly at `http://127.0.0.1:8000/api`; for a backend on a different address, update `NEXT_PUBLIC_API_URL` in `frontend/.env.local` (for example, `http://127.0.0.1:5000/api`) and restart Next.js.

## 4. Git setup
```bash
git init
git add .
git commit -m "Build collaborative project management starter"
```
Create an empty GitHub repository and follow GitHub's instructions to add a remote and push.

## Current implementation notes
- The frontend is a polished dashboard with project/task overview and demo interactions.
- The backend includes login, role-aware project/task APIs, comments, and version-based conflict checks (409).
- The frontend dashboard currently uses sample presentation data; connect it to the API by using the documented `/api` routes or extend `frontend/src/lib/api.ts`.
- Backend creates tables on startup for quick local setup. For a longer-lived project, add Alembic migrations and tests.
- FastAPI enforces access rules server-side; still test every role against direct API calls before submission.
