import { useState } from "react";
import LANGUAGES from "../data/languages";
import { pipeline } from "../services/api";

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

  function chooseFile(nextFile) {
    setFile(nextFile || null);
    setPreview(nextFile ? URL.createObjectURL(nextFile) : "");
    setResult(null);
    setError("");
  }

  async function run() {
    if (!file && !manualText.trim()) {
      setError("Upload an image or paste text first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await pipeline(file, targetLang, manualText.trim());
      setResult(response);
    } catch (err) {
      setError(err.message || "Pipeline failed. Paste text directly if OCR is unavailable on the server.");
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
          <p>Use image OCR when the server supports it, or paste text directly for a reliable no-OCR workflow.</p>
        </div>
        <select value={targetLang} onChange={(event) => setTargetLang(event.target.value)}>
          {LANGUAGES.map((language) => (
            <option key={language.code} value={language.code}>Translate to {language.name}</option>
          ))}
        </select>
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
                <p>Click to upload PNG, JPG, JPEG, or WEBP</p>
              </div>
            )}
            <input type="file" accept="image/*" hidden onChange={(event) => chooseFile(event.target.files?.[0])} />
          </label>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title">Text Fallback</div>
            <div className="badge-live"><span className="dot" />Recommended</div>
          </div>
          <textarea
            className="textarea-main"
            value={manualText}
            onChange={(event) => setManualText(event.target.value)}
            placeholder="Paste document text here. This works even when Tesseract OCR is not installed."
          />
        </div>
      </section>

      <div className="action-row">
        <button type="button" className="btn btn-ghost" onClick={() => { chooseFile(null); setManualText(""); setResult(null); }}>
          Clear
        </button>
        <div className="spacer" />
        <button type="button" className="btn btn-primary" onClick={run} disabled={loading}>
          {loading ? "Running pipeline..." : "Run Pipeline"}
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
