Render deployment steps and required environment variables

1) Build & deploy backend

- In Render dashboard create a new Web Service (Python)
  - Environment: Python 3.x
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn app:app`
  - Root Directory: `backend` (if you set Backend as subdirectory, ensure build/install runs in that folder)

- Required environment variables (set these in Render's UI or via `render.yaml`):
  - `MONGO_URI` — MongoDB connection string
  - `MONGO_DB_NAME` — Database name (default: smarttextbot)
  - `JWT_SECRET_KEY` — Secure random secret for JWT signing
  - `GROQ_API_KEY` — (optional) API key for Groq if used
  - `ALLOWED_ORIGINS` — Comma-separated allowed origins for CORS (frontend URL)
  - `LOG_LEVEL` — e.g., INFO

2) Build & deploy frontend

- In Render dashboard create a new Static Site
  - Build Command: `npm install && npm run build`
  - Publish Directory: `frontend/dist` or `frontend/build` depending on your bundler
  - Set environment variable `VITE_API_BASE_URL` to your backend URL (e.g., `https://smart-text-bot-backend.onrender.com`)

3) CORS & secrets

- Ensure `ALLOWED_ORIGINS` includes the frontend site URL and any preview domains.
- Keep `JWT_SECRET_KEY` secret and never commit it to Git.

4) Verify

- After deployment, visit the frontend URL and test endpoints (signup/login/translate/summarize).
- Use `/health` endpoint on the backend to confirm.
