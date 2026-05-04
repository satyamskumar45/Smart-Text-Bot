Frontend OCR (Tesseract.js)

Overview

This project uses Tesseract.js in the browser to extract text from uploaded images. OCR is performed entirely on the client — the backend pipeline expects only text input and is unchanged.

Quick install

Run in the frontend folder:

```bash
npm install tesseract.js
```

How it works

- Upload image on the Document Pipeline page.
- The browser auto-runs Tesseract.js and shows a progress bar.
- Extracted text is placed into the "Extracted Text (Editable)" textarea — you can edit it.
- Click "Run Pipeline" to send the text to the backend using the existing `/pipeline` endpoint (text only).

Notes

- OCR language can be selected on the page (defaults to English).
 - OCR language can be selected on the page (English and Hindi supported by default).
- Large images are downscaled in the browser to improve performance.
- No backend Tesseract dependency is required for OCR when using the frontend flow.

Performance

- Workers are cached per language to avoid re-initialization and improve subsequent OCR speed.
- If you want to free resources, call `terminateAllWorkers()` exported from `frontend/src/utils/ocr.js`.

Troubleshooting

- If OCR fails or produces low-quality results, try a clearer, higher-contrast image or select the correct OCR language.
- If you want additional OCR languages, update `frontend/src/pages/Pipeline.jsx` OCR_LANGS list.

Files

- `frontend/src/utils/ocr.js` — OCR utility using Tesseract.js
- `frontend/src/pages/Pipeline.jsx` — UI integration and workflow
- `frontend/src/style.css` — minimal spinner/visual styles

