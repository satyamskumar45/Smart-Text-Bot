import { useState } from "react";
import { translate } from "../services/api";

export default function Translate() {
  const [fromLang, setFromLang] = useState("en");
  const [toLang, setToLang] = useState("hi");
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const swap = () => {
    setFromLang(toLang);
    setToLang(fromLang);
    setInput(output);
    setOutput(input);
  };

  const run = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setOutput("");
    try {
      const r = await translate(input, fromLang, toLang);
      setOutput(r.data.translated);
    } catch {
      setOutput("⚠ Translation failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    if (!output) return;
    await navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="translate-layout">
      <div className="page-header">
        <h1>Translation</h1>
        <p>Translate text between languages using AI-powered language models.</p>
      </div>

      <div className="card">
        {/* Header */}
        <div className="card-header">
          <div className="card-title">
            <span className="card-title-icon">⇄</span>
            Language Translation
          </div>
          <div className="badge-live">
            <span className="dot" />
            Live
          </div>
        </div>

        {/* Lang Selector */}
        <div className="lang-row">
          <input
            className="lang-select"
            value={fromLang}
            onChange={(e) => setFromLang(e.target.value)}
            placeholder="From (e.g. en)"
          />
          <button className="swap-btn" onClick={swap} title="Swap languages">
            ⇄
          </button>
          <input
            className="lang-select"
            value={toLang}
            onChange={(e) => setToLang(e.target.value)}
            placeholder="To (e.g. hi)"
          />
        </div>

        {/* Dual text area */}
        <div className="dual-area">
          <div className="dual-pane">
            <div className="dual-pane-label">Source · {fromLang.toUpperCase()}</div>
            <textarea
              className="textarea-main"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter text to translate…"
            />
          </div>
          <div className="dual-area-divider" />
          <div className="dual-pane">
            <div className="dual-pane-label">Translation · {toLang.toUpperCase()}</div>
            <textarea
              className="textarea-output"
              value={output}
              readOnly
              placeholder={loading ? "Translating…" : "Translation will appear here…"}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="action-row">
          <button className="btn btn-ghost btn-icon" onClick={copy} title="Copy translation">
            {copied ? "✓" : "⎘"}
          </button>
          <div className="spacer" />
          <button
            className="btn btn-primary"
            onClick={run}
            disabled={loading || !input.trim()}
          >
            {loading ? (
              <>
                <div className="spinner" /> Translating…
              </>
            ) : (
              <>🚀 Translate</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}