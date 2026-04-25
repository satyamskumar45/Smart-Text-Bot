import { useState } from "react";
import { contextTransform } from "../services/api";

const TONES = [
  { key: "formal", label: "Formal", desc: "Official and respectful writing", color: "#4f8ef7" },
  { key: "professional", label: "Professional", desc: "Business-ready communication", color: "#63d2be" },
  { key: "academic", label: "Academic", desc: "Research and scholarly voice", color: "#a78bfa" },
  { key: "casual", label: "Casual", desc: "Friendly, relaxed wording", color: "#f5a623" },
  { key: "persuasive", label: "Persuasive", desc: "Convincing, action-oriented language", color: "#ff5b6a" },
];

export default function ContextEngine() {
  const [text, setText] = useState("");
  const [tone, setTone] = useState("professional");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult("");
    setError("");
    try {
      const response = await contextTransform(text, tone);
      setResult(response.transformed);
    } catch (err) {
      setError(err.message || "Context transformation failed");
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    if (!result) return;
    await navigator.clipboard.writeText(result);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  };

  const selectedTone = TONES.find((item) => item.key === tone);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div className="page-header">
        <h1>Context Engine</h1>
        <p>Rewrite text into formal, professional, academic, casual, or persuasive styles with real saved output.</p>
      </div>

      {error && (
        <div className="card" style={{ borderColor: "var(--error, #ff5b6a)" }}>
          <p style={{ margin: 0, color: "var(--error, #ff5b6a)" }}>{error}</p>
        </div>
      )}

      <div className="tone-grid">
        {TONES.map((item) => (
          <button
            key={item.key}
            className={`tone-card ${tone === item.key ? "selected" : ""}`}
            style={tone === item.key ? { borderColor: item.color, background: `${item.color}12` } : {}}
            onClick={() => {
              setTone(item.key);
              setResult("");
              setError("");
            }}
          >
            <div className="tone-card-label" style={tone === item.key ? { color: item.color } : {}}>
              {item.label}
            </div>
            <div className="tone-card-desc">{item.desc}</div>
          </button>
        ))}
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <span className="card-title-icon">CX</span>
            Transform to {selectedTone?.label}
          </div>
          <div className="badge-live">
            <span className="dot" />
            Live
          </div>
        </div>

        <div className="dual-area" style={{ marginBottom: 16 }}>
          <div className="dual-pane">
            <div className="dual-pane-label">Original Text</div>
            <textarea
              className="dual-pane textarea-main"
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="Enter text to transform..."
              style={{ border: "none", borderRadius: 0, minHeight: 160, background: "transparent" }}
            />
          </div>
          <div className="dual-area-divider" />
          <div className="dual-pane">
            <div className="dual-pane-label">{selectedTone?.label} Version</div>
            <div className="dual-pane-output">
              {loading ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 8, padding: "14px 16px" }}>
                  <div className="skeleton-line" />
                  <div className="skeleton-line" />
                  <div className="skeleton-line short" />
                </div>
              ) : result ? (
                <p style={{ padding: "14px 16px", fontSize: 14, lineHeight: 1.7, color: "var(--text)" }}>{result}</p>
              ) : (
                <p style={{ padding: "14px 16px", fontSize: 14, color: "var(--text-3)" }}>
                  Transformed text will appear here...
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="action-row">
          {result && (
            <button className="btn btn-ghost btn-icon" onClick={copy} title="Copy">
              {copied ? "OK" : "CP"}
            </button>
          )}
          <div className="spacer" />
          <button className="btn btn-primary" onClick={run} disabled={loading || !text.trim()}>
            {loading ? "Transforming..." : "Transform"}
          </button>
        </div>
      </div>
    </div>
  );
}
