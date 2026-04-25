import { useState } from "react";
import { summarize, summarizeDocument } from "../services/api";

export default function Summarizer() {
  const [text, setText] = useState("");
  const [mode, setMode] = useState("short");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copiedKey, setCopiedKey] = useState(null);

  const runTextSummary = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);
    setError("");
    try {
      const response = await summarize(text, mode);
      setResult(response);
    } catch (err) {
      console.error("[SUMMARIZE ERROR]", err);
      setError(err.message || "Summarization failed");
    } finally {
      setLoading(false);
    }
  };

  const runDocumentSummary = async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);
    setError("");
    try {
      const response = await summarizeDocument(file, mode);
      setResult(response);
    } catch (err) {
      console.error("[DOCUMENT SUMMARIZE ERROR]", err);
      setError(err.message || "Document summarization failed");
    } finally {
      setLoading(false);
    }
  };

  const copy = async (value, key) => {
    if (!value) return;
    await navigator.clipboard.writeText(value);
    setCopiedKey(key);
    window.setTimeout(() => setCopiedKey(null), 1500);
  };

  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div className="page-header">
        <h1>Text Summarizer</h1>
        <p>Summarize pasted text or uploaded documents with short and detailed summary modes.</p>
      </div>

      <div className="mode-tabs">
        {[
          { key: "short", label: "Short Summary", desc: "Fast paragraph plus key bullets" },
          { key: "detailed", label: "Detailed Summary", desc: "Deeper explanation and richer recap" },
        ].map((item) => (
          <button
            key={item.key}
            className={`mode-tab ${mode === item.key ? "active" : ""}`}
            onClick={() => setMode(item.key)}
          >
            <div>
              <div className="mode-tab-label">{item.label}</div>
              <div className="mode-tab-desc">{item.desc}</div>
            </div>
          </button>
        ))}
      </div>

      {error && (
        <div className="card" style={{ borderColor: "var(--error, #ff5b6a)" }}>
          <p style={{ margin: 0, color: "var(--error, #ff5b6a)" }}>{error}</p>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <span className="card-title-icon">TX</span>
            Text Summary
          </div>
          <div className="badge-live">
            <span className="dot" />
            Live
          </div>
        </div>
        <textarea
          className="textarea-main"
          style={{ height: 200 }}
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Paste article, notes, transcript, or any long text here..."
        />
        <div className="action-row" style={{ marginTop: 16 }}>
          <span style={{ fontSize: 12, color: "var(--text-3)", fontFamily: "var(--font-mono)" }}>
            {wordCount} words
          </span>
          <div className="spacer" />
          <button className="btn btn-primary" onClick={runTextSummary} disabled={loading || !text.trim()}>
            {loading ? "Summarizing..." : "Summarize Text"}
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <span className="card-title-icon">DOC</span>
            Document Summary
          </div>
          <div className="badge-live">
            <span className="dot" />
            Text files only
          </div>
        </div>
        <input
          type="file"
          accept=".txt,.md,.csv,.json,.log"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
        <div className="action-row" style={{ marginTop: 16 }}>
          <span style={{ fontSize: 12, color: "var(--text-3)" }}>
            {file ? file.name : "Upload a text-based document"}
          </span>
          <div className="spacer" />
          <button className="btn btn-primary" onClick={runDocumentSummary} disabled={loading || !file}>
            {loading ? "Summarizing..." : "Summarize Document"}
          </button>
        </div>
      </div>

      {result && (
        <div className="summarizer-results" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <span className="card-title-icon">SM</span>
                Summary
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => copy(result.summary, "summary")}>
                {copiedKey === "summary" ? "OK" : "CP"}
              </button>
            </div>
            <p style={{ fontSize: 14, lineHeight: 1.8, color: "var(--text-2)" }}>{result.summary}</p>
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <span className="card-title-icon">DT</span>
                Detailed Summary
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => copy(result.detailed_summary, "detail")}>
                {copiedKey === "detail" ? "OK" : "CP"}
              </button>
            </div>
            <p style={{ fontSize: 14, lineHeight: 1.8, color: "var(--text-2)" }}>
              {result.detailed_summary}
            </p>
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <span className="card-title-icon">KP</span>
                Key Points
              </div>
              <button
                className="btn btn-ghost btn-icon"
                onClick={() => copy((result.bullets || []).join("\n"), "bullets")}
              >
                {copiedKey === "bullets" ? "OK" : "CP"}
              </button>
            </div>
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
