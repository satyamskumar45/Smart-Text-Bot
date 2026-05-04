import { useState, useRef, useEffect } from "react";
import LANGUAGES from "../data/languages";
const OCR_LANGS = [
  { code: "eng", label: "English" },
  { code: "hin", label: "Hindi" },
];
import { pipeline } from "../services/api";
import { extractTextFromImage, terminateAllWorkers } from "../utils/ocr";

const STEPS = [
  ["Input", "Upload image or paste text"],
  ["Structure", "Clean and organize content"],
  ["Translate", "Convert to target language"],
  ["Summarize", "Create a compact recap"],
];

export default function Pipeline() {
  const [file, setFile] = useState(null);
  const [manualText, setManualText] = useState("");
  const [preview, setPreview] = useState("");
  const [targetLang, setTargetLang] = useState("en");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrProgress, setOcrProgress] = useState(0);
  const [ocrError, setOcrError] = useState("");
  const [ocrLang, setOcrLang] = useState(() => {
    try {
      return localStorage.getItem("ocrLang") || "eng";
    } catch (e) {
      return "eng";
    }
  });
  const textareaRef = useRef(null);

  function chooseFile(nextFile) {
    setFile(nextFile || null);
    setPreview(nextFile ? URL.createObjectURL(nextFile) : "");
    setResult(null);
    setError("");
    setOcrError("");
    setOcrProgress(0);

    // Kick off OCR asynchronously (non-blocking)
    if (nextFile) {
      runOcr(nextFile);
    }
  }

  useEffect(() => {
    // persist selected OCR language
    try {
      localStorage.setItem("ocrLang", ocrLang);
    } catch (e) {}
  }, [ocrLang]);

  useEffect(() => {
    // terminate workers when component unmounts to free memory
    return () => {
      try {
        terminateAllWorkers();
      } catch (e) {}
    };
  }, []);

  async function runOcr(imageFile) {
    setOcrLoading(true);
    setOcrProgress(0);
    setOcrError("");
    try {
      const text = await extractTextFromImage(imageFile, (pct) => {
        setOcrProgress(pct);
        }, ocrLang);
      // Put extracted text into the editable textarea so user can adjust before sending
      setManualText((prev) => (prev && prev.trim() ? prev : text));
      // Smooth scroll to textarea and focus so user can edit
      setTimeout(() => {
        try {
          if (textareaRef.current) {
            textareaRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
            textareaRef.current.focus();
          }
        } catch (e) {
          // ignore
        }
      }, 150);
    } catch (err) {
      setOcrError(err?.message || "OCR failed. Try a different image.");
    } finally {
      setOcrLoading(false);
      setOcrProgress(100);
    }
  }

  async function run() {
    if (ocrLoading) {
      setError("Please wait for OCR to finish before running the pipeline.");
      return;
    }

    if (!manualText.trim()) {
      setError("Please enter or extract text first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Send extracted/edited text to backend pipeline. If we have manualText, prefer that
      // and don't require sending the image file to the server.
      const response = await pipeline(null, targetLang, manualText.trim());
      setResult(response);
    } catch (err) {
      setError(err.message || "Pipeline failed. Try again or paste text directly.");
    } finally {
      setLoading(false);
    }
  }

  function copy(value) {
    if (value) {
      navigator.clipboard.writeText(value);
    }
  }

  return (
    <div className="pipeline-page">
      <section className="pipeline-hero">
        <div>
          <div className="hero-eyebrow">
            <span className="hero-eyebrow-dot" />
            Document Pipeline
          </div>
          <h1>Turn messy input into translated, summarized knowledge.</h1>
          <p>Browser OCR: upload an image to extract editable text locally, then send text to the pipeline.</p>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <select value={targetLang} onChange={(event) => setTargetLang(event.target.value)}>
          {LANGUAGES.map((language) => (
            <option key={language.code} value={language.code}>Translate to {language.name}</option>
          ))}
          </select>

          <div>
            <label style={{ fontSize: 12, color: "#6b7280" }}>OCR language</label>
            <select value={ocrLang} onChange={(e) => setOcrLang(e.target.value)} style={{ display: "block" }}>
              {OCR_LANGS.map((l) => (
                <option key={l.code} value={l.code}>{l.label}</option>
              ))}
            </select>
          </div>
        </div>
      </section>

      <div className="pipeline-timeline">
        {STEPS.map(([title, desc], index) => (
          <div key={title} className="pipeline-step-card">
            <strong>{index + 1}</strong>
            <span>{title}</span>
            <p>{desc}</p>
          </div>
        ))}
      </div>

      {error ? <div className="auth-error">{error}</div> : null}

      <section className="pipeline-input-grid">
        <div className="card">
          <div className="card-header">
            <div className="card-title">Image Input</div>
            <div className="badge-live"><span className="dot" />Optional</div>
          </div>
          <label className="upload-zone">
            {preview ? (
              <div className="upload-preview">
                <img src={preview} alt="preview" className="preview-img" />
                <div className="upload-filename">{file?.name}</div>
              </div>
            ) : (
              <div className="upload-empty">
                <div>IMG</div>
                <p>Click to upload PNG, JPG, JPEG, or WEBP — OCR runs in your browser</p>
              </div>
            )}
            <input
              type="file"
              accept="image/*"
              hidden
              onChange={(event) => chooseFile(event.target.files?.[0])}
              disabled={ocrLoading || loading}
            />
          </label>

          <div className="mt-3">
            {ocrLoading ? (
              <div className="w-full">
                <div className="text-sm mb-1"><span className="spinner" /> Extracting text... {ocrProgress}%</div>
                <div className="w-full bg-gray-200 rounded h-2 overflow-hidden">
                  <div
                    className="bg-teal-500 h-2"
                    style={{ width: `${Math.min(100, ocrProgress)}%`, transition: "width 120ms linear" }}
                  />
                </div>
              </div>
            ) : ocrError ? (
              <div className="auth-error">{ocrError}</div>
            ) : ocrProgress > 0 && ocrProgress < 100 ? (
              <div className="text-sm">OCR progress: {ocrProgress}%</div>
            ) : (
              <div className="text-sm text-gray-600">{preview ? "Ready" : "No image selected"}</div>
            )}

            <div className="mt-2 flex items-center gap-2">
              {preview ? (
                <>
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={() => {
                      // remove image but keep any extracted text
                      setFile(null);
                      setPreview("");
                      setOcrProgress(0);
                      setOcrError("");
                    }}
                    disabled={ocrLoading || loading}
                  >
                    Remove Image
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={() => runOcr(file)}
                    disabled={ocrLoading || loading}
                  >
                    Re-run OCR
                  </button>
                    <button
                      type="button"
                      className="btn btn-ghost"
                      onClick={() => navigator.clipboard.writeText(manualText || "")}
                      disabled={!manualText}
                    >
                      Copy Text
                    </button>
                </>
              ) : null}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
              <div className="card-title">Extracted Text (Editable)</div>
              <div className="badge-live"><span className="dot" />Editable</div>
            </div>
            <textarea
              ref={textareaRef}
              className="textarea-main"
              value={manualText}
              onChange={(event) => setManualText(event.target.value)}
              placeholder="Extracted text will appear here. You can edit before sending."
              disabled={ocrLoading || loading}
            />
        </div>
      </section>

      <div className="action-row">
          <button type="button" className="btn btn-ghost" onClick={() => { setFile(null); setPreview(""); setManualText(""); setResult(null); }} disabled={ocrLoading || loading}>
            Clear
          </button>
        <div className="spacer" />
          <button type="button" className="btn btn-primary" onClick={run} disabled={loading || ocrLoading}>
            {loading ? "Processing..." : ocrLoading ? `Extracting... ${ocrProgress}%` : "Run Pipeline"}
        </button>
      </div>

      {result ? (
        <section className="pipeline-results">
          {[
            ["Extracted Text", result.extracted_text],
            ["Translation", result.translation],
            ["Summary", result.summary],
          ].map(([title, value]) => (
            <article key={title} className="card">
              <div className="card-header">
                <div className="card-title">{title}</div>
                <button type="button" className="btn btn-ghost" onClick={() => copy(value)}>Copy</button>
              </div>
              <div className="result-textbox">{value || "-"}</div>
            </article>
          ))}
          {result.bullets?.length ? (
            <article className="card">
              <div className="card-title">Key Points</div>
              <ul className="bullet-list">
                {result.bullets.map((bullet, index) => <li key={`${bullet}-${index}`}>{bullet}</li>)}
              </ul>
            </article>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}
