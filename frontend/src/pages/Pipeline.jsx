import { useState } from "react";
import { pipeline } from "../services/api";
import LANGUAGES from "../data/languages";

const STEPS = [
  { key: "ocr", label: "OCR Extraction", desc: "Read text from the uploaded image" },
  { key: "translate", label: "Translation", desc: "Convert the content to the target language" },
  { key: "summarize", label: "Summarization", desc: "Generate a compact readable recap" },
];

export default function Pipeline() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [targetLang, setTargetLang] = useState("en");
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(null);
  const [result, setResult] = useState(null);
  const [copiedKey, setCopiedKey] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");

  const handleFile = (file) => {
    if (!file) return;
    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError("");
  };

  const run = async () => {
    if (!image) return;
    setLoading(true);
    setResult(null);
    setError("");

    for (const step of STEPS) {
      setActiveStep(step.key);
      await new Promise((resolve) => window.setTimeout(resolve, 250));
    }

    try {
      const response = await pipeline(image, targetLang);
      setResult(response);
    } catch (err) {
      console.error("[PIPELINE ERROR]", err);
      setError(err.message || "Pipeline failed");
    } finally {
      setLoading(false);
      setActiveStep(null);
    }
  };

  const copy = async (value, key) => {
    if (!value) return;
    await navigator.clipboard.writeText(value);
    setCopiedKey(key);
    window.setTimeout(() => setCopiedKey(null), 1500);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div className="page-header">
        <h1>Document Pipeline</h1>
        <p>Upload an image, extract the text, translate it, and generate a summary in one connected flow.</p>
      </div>

      {error && (
        <div className="card" style={{ borderColor: "var(--error, #ff5b6a)" }}>
          <p style={{ margin: 0, color: "var(--error, #ff5b6a)" }}>{error}</p>
        </div>
      )}

      <div className="pipeline-steps">
        {STEPS.map((step, index) => (
          <div key={step.key} style={{ display: "flex", alignItems: "center", gap: 0 }}>
            <div className={`pipeline-step ${activeStep === step.key ? "active" : result ? "done" : ""}`}>
              <div className="step-icon">{result ? "OK" : step.label.slice(0, 2)}</div>
              <div>
                <div className="step-label">{step.label}</div>
                <div className="step-desc">{step.desc}</div>
              </div>
            </div>
            {index < STEPS.length - 1 && <div className="step-connector" />}
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <span className="card-title-icon">DP</span>
            Image Upload
          </div>
          <select
            className="lang-select lang-select-dropdown"
            value={targetLang}
            onChange={(event) => setTargetLang(event.target.value)}
            style={{ width: "auto", minWidth: 180 }}
          >
            {LANGUAGES.map((language) => (
              <option key={language.code} value={language.code}>
                Translate to: {language.name}
              </option>
            ))}
          </select>
        </div>

        <div
          className={`upload-zone ${dragOver ? "drag-over" : ""} ${image ? "has-file" : ""}`}
          onDragOver={(event) => {
            event.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragOver(false);
            handleFile(event.dataTransfer.files?.[0]);
          }}
          onClick={() => document.getElementById("pipeline-file-input").click()}
        >
          {preview ? (
            <div className="upload-preview">
              <img src={preview} alt="preview" className="preview-img" />
              <div className="upload-filename">{image?.name}</div>
            </div>
          ) : (
            <div className="upload-empty">
              <div style={{ fontSize: 40, opacity: 0.4 }}>IMG</div>
              <div style={{ fontSize: 14, color: "var(--text-2)", marginTop: 8 }}>
                Drag and drop an image or click to browse
              </div>
              <div style={{ fontSize: 12, color: "var(--text-3)" }}>PNG, JPG, JPEG, WEBP</div>
            </div>
          )}
          <input
            id="pipeline-file-input"
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={(event) => handleFile(event.target.files?.[0])}
          />
        </div>

        <div className="action-row" style={{ marginTop: 16 }}>
          {image && (
            <button
              className="btn btn-ghost"
              onClick={() => {
                setImage(null);
                setPreview(null);
                setResult(null);
                setError("");
              }}
            >
              Clear
            </button>
          )}
          <div className="spacer" />
          <button className="btn btn-primary" onClick={run} disabled={loading || !image}>
            {loading ? "Processing..." : "Run Pipeline"}
          </button>
        </div>
      </div>

      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <span className="card-title-icon">OCR</span>
                Extracted Text
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => copy(result.extracted_text, "ocr")}>
                {copiedKey === "ocr" ? "OK" : "CP"}
              </button>
            </div>
            <div className="result-textbox">{result.extracted_text}</div>
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <span className="card-title-icon">TR</span>
                Translation
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => copy(result.translation, "translation")}>
                {copiedKey === "translation" ? "OK" : "CP"}
              </button>
            </div>
            <div className="result-textbox">{result.translation}</div>
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <span className="card-title-icon">SU</span>
                Summary
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => copy(result.summary, "summary")}>
                {copiedKey === "summary" ? "OK" : "CP"}
              </button>
            </div>
            <p style={{ fontSize: 14, lineHeight: 1.8, color: "var(--text-2)", marginBottom: 16 }}>{result.summary}</p>
            <ul className="bullet-list">
              {(result.bullets || []).map((bullet, index) => (
                <li key={`${bullet}-${index}`} className="bullet-item">
                  {bullet}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
