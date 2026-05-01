import { useState, useRef } from "react";
import { writing } from "../services/api";

const MODES = [
  { key: "grammar", label: "Grammar Fix", desc: "Fix spelling, grammar, and punctuation" },
  { key: "tone", label: "Tone Rewrite", desc: "Switch to a targeted communication style" },
  { key: "rewrite", label: "Rewrite", desc: "Restructure text for clarity and flow" },
];

const TONES = [
  { key: "professional", label: "Professional" },
  { key: "simple", label: "Simple" },
  { key: "formal", label: "Formal" },
  { key: "friendly", label: "Friendly" },
];

export default function WritingAssistant() {
  const [text, setText] = useState("");
  const [mode, setMode] = useState("grammar");
  const [toneStyle, setToneStyle] = useState("professional");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef(null);

  const resizeTextarea = (element) => {
    if (!element) return;
    element.style.height = "auto";
    element.style.height = `${Math.max(element.scrollHeight, 180)}px`;
  };

  const handleTextChange = (event) => {
    setText(event.target.value);
    resizeTextarea(event.target);
  };

  const run = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);
    setError("");
    try {
      const response = await writing(text, mode, toneStyle);
      setResult(response);
    } catch (err) {
      console.error("[WRITING ASSISTANT ERROR]", err);
      setError(err.message || "Writing assistant request failed");
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    if (!result?.result) return;
    await navigator.clipboard.writeText(result.result);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  };

  const renderResultParagraphs = (value) => {
    if (!value) return null;
    return value
      .trim()
      .split(/\n{2,}/)
      .map((paragraph, index) => (
        <p key={index} className="result-paragraph">
          {paragraph.split("\n").reduce((acc, line, lineIndex) => {
            if (lineIndex > 0) acc.push(<br key={lineIndex} />);
            acc.push(line);
            return acc;
          }, [])}
        </p>
      ));
  };

  return (
    <div className="writing-page">
      <div className="page-header">
        <h1>Writing Assistant</h1>
        <p>Elevate your draft with grammar correction, rewriting, and tone refinement in one polished workflow.</p>
      </div>

      <div className="writing-panel card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <span className="card-title-icon">WR</span>
              {MODES.find((item) => item.key === mode)?.label}
            </div>
            <p className="card-subtitle">Write with clarity, confidence, and consistent tone.</p>
          </div>

          {mode === "tone" ? (
            <select
              className="lang-select lang-select-dropdown"
              value={toneStyle}
              onChange={(event) => setToneStyle(event.target.value)}
            >
              {TONES.map((tone) => (
                <option key={tone.key} value={tone.key}>
                  {tone.label} tone
                </option>
              ))}
            </select>
          ) : null}
        </div>

        <div className="mode-tabs">
          {MODES.map((item) => (
            <button
              key={item.key}
              className={`mode-tab ${mode === item.key ? "active" : ""}`}
              onClick={() => {
                setMode(item.key);
                setResult(null);
                setError("");
              }}
            >
              <div className="mode-tab-icon">{item.label.charAt(0)}</div>
              <div>
                <div className="mode-tab-label">{item.label}</div>
                <div className="mode-tab-desc">{item.desc}</div>
              </div>
            </button>
          ))}
        </div>

        <div className="input-group">
          <label className="input-label" htmlFor="writing-input">
            Draft text
          </label>
          <textarea
            id="writing-input"
            ref={textareaRef}
            className="textarea-main writing-input"
            rows={8}
            value={text}
            onChange={handleTextChange}
            placeholder="Paste your draft here, then choose a mode and refine your message."
          />
        </div>

        <div className="action-row">
          <span className="input-hint">No text? Add your writing sample to get started.</span>
          <button className="btn btn-primary btn-full" onClick={run} disabled={loading || !text.trim()}>
            {loading ? "Processing..." : "Run Assistant"}
          </button>
        </div>
      </div>

      {error && (
        <div className="card error-card">
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div className="writing-output-grid">
          <div className="card output-card">
            <div className="card-header">
              <div>
                <div className="card-title">
                  <span className="card-title-icon">OK</span>
                  Improved Text
                </div>
                <p className="card-subtitle">Copy or review the polished version below.</p>
              </div>
              <button className="btn btn-copy" onClick={copy}>
                {copied ? "Copied" : "Copy text"}
              </button>
            </div>
            <div className="result-textbox polished-output">
              {renderResultParagraphs(result.result)}
            </div>
          </div>

          <div className="card changes-card">
            <div className="card-header">
              <div>
                <div className="card-title">
                  <span className="card-title-icon">CH</span>
                  Changes Made
                </div>
                <p className="card-subtitle">See the most important edits and improvements.</p>
              </div>
            </div>
            <ul className="changes-list">
              {(result.changes || []).length ? (
                result.changes.map((change, index) => (
                  <li key={`${change}-${index}`} className="change-item">
                    <span className="change-dot" />
                    <span>{change}</span>
                  </li>
                ))
              ) : (
                <li className="change-item">
                  <span className="change-dot" />
                  <span>Your draft is already polished with strong clarity and tone.</span>
                </li>
              )}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
