# Technical Documentation

## Overview

This document captures the developer-facing architecture, API flow, translation engine logic, Language Quest design, document pipeline, error handling, and performance considerations for SmartTextBot.

## Backend Architecture

### Core Components

- `backend/app.py` — Flask application entry point
- `backend/routes/` — Thin route handlers for each API module
- `backend/services/` — Business logic and AI integration
- `backend/config/` — Centralized prompt templates and settings
- `backend/utils/` — Response formatting, validation, and helpers
- `backend/middleware/` — Global error handling and request middleware
- `backend/database/` — Database connection layer (present for future persistence)

### Route Layer

The backend exposes routes for:

- `/translate` — text translation
- `/explain` — translation explanation
- `/sentiment` — sentiment analysis
- `/summarize` — text summarization
- `/grammar` — grammar and writing assistance
- `/chat` — chat assistant flow
- `/context/transform` — tone/context transformation
- `/image-scan` — OCR image upload
- `/pipeline` / `/doc-pipeline` — document pipeline flows

Routes perform validation, call services, and return standardized API responses.

## API Flow

### Standard Response Schema

All API responses use a consistent wrapper:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

On failure:

```json
{
  "success": false,
  "data": null,
  "error": "Descriptive error message"
}
```

### Axios Client Handling

Frontend calls use `frontend/src/services/api.js`, which includes:

- `baseURL` from `VITE_API_BASE_URL`
- `timeout: 25000`
- Request logging
- Response interceptor that unwraps `data` when `success` is true
- Error handling for backend JSON errors and network failures

## Translation Engine Logic

### Groq Integration

`backend/services/groq_service.py` contains:

- `complete()` — sends chat-completion requests to Groq
- `complete_json()` — wraps, validates, and falls back when responses are not strict JSON
- `translate_text()` — specialized translation function with source/target labels

### Translation Strategy

- Use a system prompt: `You are a professional translator. Provide accurate and natural translations.`
- Use a user prompt that asks for only the translated text
- Detect source language automatically when `source_lang` is `auto`
- Return raw translated text for frontend consumption

### JSON Fallback Handling

`complete_json()` attempts to parse the Groq response as JSON. If parsing fails, it falls back to:

- a default structured object when provided
- a generic wrapper with `simple`, `professional`, and `native` fields

This preserves service stability during unpredictable model outputs.

## Language Quest System

### Frontend Implementation

`frontend/src/pages/Chat.jsx` now implements Language Quest as a polished learning experience.

Key elements:

- Language selector and active state
- Daily vocabulary challenge
- Quiz practice with XP rewards
- Vocabulary learning tracker
- Phrase favorites
- Translation practice panel
- Recent translation history saved in browser storage

### Persistence

Language Quest state is persisted in `localStorage` under `languageQuestState`.

Saved state includes:

- `xp`
- `streak`
- `lastActive`
- `streakHistory`
- `completedQuizzes`
- `learnedVocabulary`
- `favoritePhrases`
- `recentTranslations`

### Learning Design

- Quizzes reward correct answers with XP and progress tracking
- Vocabulary cards let users mark words as learned
- Favorite phrases support repeated review
- Daily streak logic rewards consistent use

## Document Pipeline Logic

The document pipeline is designed for OCR-driven content extraction followed by translation and summarization.

### Flow

1. Upload a document or image
2. OCR scans and extracts text
3. Translate extracted text as needed
4. Summarize the translated text
5. Return structured results to the frontend

### Key Components

- `backend/routes/doc_pipeline.py` — pipeline orchestration route
- `backend/services/groq_service.py` — AI calls for language tasks
- `backend/utils/ocr_preprocessing.py` and `ocr_postprocessing.py` — text cleanup helpers

## Error Handling

### Backend

- All route handlers use `utils.response.success()` and `utils.response.error()` wrappers
- Input validation returns `400` with descriptive messages
- Unexpected exceptions return `500` with developer-friendly logs
- Backend logs include debug traces for request data and failure points

### Frontend

- API client maps backend JSON errors to `error.message`
- Network failures show a clear runtime message
- Timeout handling is built into the Axios client

## OCR Flow

OCR operations use the backend image route to accept file uploads and process them through a pipeline.

Key stages:

- Image ingestion via file upload
- Preprocessing for cleaner OCR results
- Text extraction from image content
- Postprocessing for noise reduction
- Translation / summarization of extracted text

## Fallback Handling

SmartTextBot includes both AI fallback and transport fallback:

- `complete_json()` ensures JSON-safe output
- Backend catches parsing failures and returns structured fallback data
- Axios interceptors normalize API responses for the frontend
- UI components handle missing data and display empty states cleanly

## Learning System Design

### Frontend State Management

- Component state in `Chat.jsx`
- Persistent storage in `localStorage`
- UI-driven actions for quizzes, vocabulary, and favorites
- Toast notifications for progress feedback

### Backend Data Flow

- Translation and explanation requests are stateless
- The backend does not yet persist user progress permanently
- LocalStorage is used for quick, client-side persistence

## Performance Considerations

- API timeout set to 25 seconds to balance model response time and user expectation
- Minimal data payloads sent to backend routes
- Response interceptors avoid repeated data parsing overhead
- UI renders are structured into cards and sections for better performance
- Future improvement: add caching for repeated translation lookups

## Recommended Developer Notes

- Keep prompt templates centralized in `backend/config/prompts.py`
- Keep route handlers thin and delegate business logic to services
- Add unit tests for services and route validation
- Add integration tests for the full backend API contract
- Add monitoring around Groq API latency and error rates
