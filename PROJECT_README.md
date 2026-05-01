# SmartTextBot

SmartTextBot is an AI-powered language productivity platform designed for real-world learning, translation, summarization, and document intelligence.

## Project Overview

SmartTextBot brings together advanced natural language processing features in a modern single-page application:

- **Smart Translator** with real-time translation and learner-friendly explanations
- **Language Quest** for gamified learning, XP, streaks, and vocabulary tracking
- **Writing Assistant** for grammar, style, and tone improvements
- **Text Summarizer** for brief, accurate content distillation
- **Sentiment Analysis** for tone and emotional insights
- **Document Pipeline** for OCR, translation, and summarization of uploaded files
- **Context Engine** for adaptive tone transformation

## Major Features

- End-to-end **frontend + backend** AI workflow
- **Persistent progress** using browser storage for Language Quest
- **Structured AI responses** with robust fallback handling
- **Career-ready design** with polished UI and production code quality
- **Modular architecture** with clean route/service separation

## Tech Stack

- **Frontend:** React 18, Vite 5, React Router DOM, Axios
- **Backend:** Python, Flask, Groq API, dotenv
- **Data:** LocalStorage persistence for progress state
- **Deployment:** Simple backend and frontend build commands

## Architecture Overview

SmartTextBot is separated into two main applications:

- `backend/` hosts the Flask API, AI service layer, route handlers, validators, and utilities.
- `frontend/` hosts the React UI, routing, service client, and user-facing pages.

The backend exposes APIs for translation, chat, sentiment, summarization, grammar, OCR, and document pipelines. The frontend consumes these endpoints and manages UI state, persistence, and user interactions.

## Setup Instructions

### Backend

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example`:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
5. Start the backend server:
   ```bash
   python app.py
   ```

### Frontend

1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Environment Variables

Backend:

- `GROQ_API_KEY` - required API key for Groq AI access

Frontend:

- `VITE_API_BASE_URL` - optional custom backend URL, defaults to `https://smart-text-bot-backend-docker.onrender.com`

## Folder Structure

```text
backend/
  |- app.py
  |- config/
  |- core/
  |- database/
  |- middleware/
  |- routes/
  |- services/
  |- utils/
  `- requirements.txt
frontend/
  |- index.html
  |- package.json
  `- src/
     |- App.jsx
     |- main.jsx
     |- style.css
     |- services/api.js
     |- pages/
     `- data/
```

## Deployment Notes

- Build the frontend for production with `npm run build`.
- Deploy the backend using any Python-friendly host or container.
- Configure `VITE_API_BASE_URL` in the frontend deployment environment.
- Use a secure secrets store for `GROQ_API_KEY` in production.

## GitHub-Ready Restore Guide

This repository is intentionally cleaned for GitHub upload and deployment review. Reinstallable folders such as `.venv/`, `frontend/node_modules/`, and `frontend/dist/` are not included.

Restore the backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Restore the frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Create a production frontend build when needed:

```bash
cd frontend
npm install
npm run build
```

## Screenshots

> Add polished interface screenshots here once available.

## Future Improvements

- Add user accounts and cloud-based progress persistence
- Expand Language Quest with more quiz sets and levels
- Add full analytics dashboards for usage and performance
- Add multi-file document pipeline support
- Add automated testing coverage for critical APIs

## Why This Project Is Strong

SmartTextBot is built with a focus on production quality and usability. The repository reflects a clean, recruiter-friendly structure with strong separation between frontend and backend, modern AI integration, and a polished feature set for real-world language learning and productivity.
