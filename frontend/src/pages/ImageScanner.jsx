import { useState } from "react";
import { rewriteText } from "../services/api";

const MODES = [
  { key: "correct", label: "Grammar Fix" },
  { key: "formal", label: "Formal" },
  { key: "informal", label: "Informal" },
  { key: "simple", label: "Simple" },
  { key: "professional", label: "Professional" },
  { key: "academic", label: "Academic" },
  { key: "shorten", label: "Shorten" },
  { key: "expand", label: "Expand" },
];

export default function ImageScanner() {
  const [text, setText] = useState("i want to improve this sentence and make it sound better");
  const [mode, setMode] = useState("correct");
  const [result, setResult] = useState("");
  const [variants, setVariants] = useState({});
  const [loading, setLoading] = useState(false);

  async function run(selectedMode = mode) {
    if (!text.trim() || loading) {
      return;
    }

    setLoading(true);
    setResult("");

    try {
      const data = await rewriteText({ text, mode: selectedMode });
      setResult(data.corrected || "");
      setMode(selectedMode);
    } catch (error) {
      setResult(error.message || "Rewrite failed.");
    } finally {
      setLoading(false);
    }
  }

  async function generateVariants() {
    if (!text.trim() || loading) {
      return;
    }

    setLoading(true);
    setVariants({});

    try {
      const entries = await Promise.all(
        ["formal", "informal", "simple", "professional"].map(async (item) => {
          const data = await rewriteText({ text, mode: item });
          return [item, data.corrected || ""];
        })
      );
      setVariants(Object.fromEntries(entries));
    } catch (error) {
      setResult(error.message || "Could not generate variants.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grammar-workspace">
      <div className="page-header">
        <h1>Grammar & Rewriter</h1>
        <p>Fix grammar, change tone, simplify text, or reshape writing for professional use.</p>
      </div>

      <section className="card">
        <div className="rewrite-mode-row">
          {MODES.map((item) => (
            <button
              key={item.key}
              type="button"
              className={`btn ${mode === item.key ? "btn-primary" : "btn-ghost"}`}
              onClick={() => run(item.key)}
              disabled={loading}
            >
              {item.label}
            </button>
          ))}
        </div>

        <div className="dual-area">
          <div className="dual-pane">
            <div className="dual-pane-label">Original</div>
            <textarea
              className="textarea-main"
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="Paste text to improve..."
            />
          </div>
          <div className="dual-area-divider" />
          <div className="dual-pane">
            <div className="dual-pane-label">Improved</div>
            <textarea
              className="textarea-output"
              value={result}
              readOnly
              placeholder={loading ? "Working..." : "Your improved text appears here..."}
            />
          </div>
        </div>

        <div className="action-row">
          <button type="button" className="btn btn-ghost" onClick={generateVariants} disabled={loading || !text.trim()}>
            Generate Tone Pack
          </button>
          <div className="spacer" />
          <button type="button" className="btn btn-primary" onClick={() => run(mode)} disabled={loading || !text.trim()}>
            {loading ? "Rewriting..." : "Rewrite"}
          </button>
        </div>
      </section>

      <div className="variant-grid">
        {["formal", "informal", "simple", "professional"].map((key) => (
          <article key={key} className="variant-card">
            <div>
              <span>{key}</span>
              <button type="button" onClick={() => navigator.clipboard.writeText(variants[key] || "")}>Copy</button>
            </div>
            <p>{variants[key] || "Generate the tone pack to compare this rewrite."}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
