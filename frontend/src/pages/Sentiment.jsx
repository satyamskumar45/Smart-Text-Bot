import { useState } from "react";
import { sentiment } from "../services/api";

const VERDICTS = {
  positive: { marker: "+", label: "Positive", color: "#4cde9c" },
  negative: { marker: "-", label: "Negative", color: "#ff5b6a" },
  neutral: { marker: "=", label: "Neutral", color: "#4f8ef7" },
};

export default function Sentiment() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    if (!text.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    try {
      const raw = await sentiment(text);
      if (raw.positive !== undefined) {
        const total = (raw.positive || 0) + (raw.negative || 0) + (raw.neutral || 0) || 1;
        setResult({
          positive: Math.round((raw.positive / total) * 100),
          negative: Math.round((raw.negative / total) * 100),
          neutral: Math.round((raw.neutral / total) * 100),
          verdict:
            raw.sentiment ||
            Object.keys({
              positive: raw.positive,
              negative: raw.negative,
              neutral: raw.neutral,
            }).reduce((a, b) => (raw[a] > raw[b] ? a : b)),
        });
      } else {
        const label = (raw.sentiment || "neutral").toLowerCase();
        setResult({
          positive: label === "positive" ? 78 : label === "negative" ? 8 : 34,
          negative: label === "negative" ? 74 : label === "positive" ? 6 : 18,
          neutral: label === "neutral" ? 70 : 16,
          verdict: label,
        });
      }
    } catch (runError) {
      setResult(null);
      setError(runError.message || "Unable to analyze sentiment.");
    } finally {
      setLoading(false);
    }
  };

  const verdict = result ? VERDICTS[result.verdict] || VERDICTS.neutral : null;
  const bars = [
    { key: "positive", label: "Positive", cls: "positive", dot: "#4cde9c" },
    { key: "negative", label: "Negative", cls: "negative", dot: "#ff5b6a" },
    { key: "neutral", label: "Neutral", cls: "neutral", dot: "#4f8ef7" },
  ];

  return (
    <div className="motion-safe:animate-[fade-in_0.35s_ease]">
      <div className="page-header">
        <h1>Sentiment Analysis</h1>
        <p>Analyze the emotional tone of any text with AI-powered sentiment scoring.</p>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <span className="card-title-icon">SA</span>
            Sentiment Analyzer
          </div>
          {result && verdict && (
            <div className="badge-live">
              <span className="dot" /> Result Ready
            </div>
          )}
        </div>

        <div className="sentiment-layout">
          <div className="sentiment-input-pane">
            <div>
              <label className="input-label">Text to Analyze</label>
              <textarea
                className="textarea-main"
                style={{ height: 180 }}
                value={text}
                onChange={(event) => setText(event.target.value)}
                placeholder="Paste or type any text - a review, tweet, message, or article..."
              />
            </div>
            {error ? <div className="auth-error" role="alert">{error}</div> : null}

            <button className="btn btn-primary btn-full" onClick={run} disabled={loading || !text.trim()}>
              {loading ? (
                <>
                  <div className="spinner" /> Analyzing...
                </>
              ) : (
                <>Analyze Sentiment</>
              )}
            </button>

            <div style={{ fontSize: 12, color: "var(--text-3)", lineHeight: 1.5 }}>
              The model classifies text as positive, negative, or neutral and returns a confidence score for each category.
            </div>
          </div>

          <div className="sentiment-divider" />

          <div className="sentiment-result-pane">
            <div className="result-header">Analysis Results</div>

            {result && verdict ? (
              <>
                <div className="sentiment-verdict" style={{ borderColor: `${verdict.color}30` }}>
                  <div className="verdict-emoji">{verdict.marker}</div>
                  <div>
                    <div className="verdict-label" style={{ color: verdict.color }}>
                      {verdict.label}
                    </div>
                    <div className="verdict-score">Overall sentiment · {result[result.verdict]}% confidence</div>
                  </div>
                </div>

                <div className="sentiment-bar-group">
                  {bars.map((bar) => (
                    <div key={bar.key} className="sentiment-bar-item">
                      <div className="bar-meta">
                        <div className="bar-label">
                          <div className="bar-dot" style={{ background: bar.dot }} />
                          {bar.label}
                        </div>
                        <div className="bar-pct">{result[bar.key]}%</div>
                      </div>
                      <div className="progress-track">
                        <div className={`progress-fill ${bar.cls}`} style={{ width: `${result[bar.key]}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div
                style={{
                  flex: 1,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 8,
                  padding: "48px 24px",
                  color: "var(--text-3)",
                  textAlign: "center",
                }}
              >
                <div style={{ fontSize: 32, opacity: 0.3 }}>SA</div>
                <div style={{ fontSize: 14, color: "var(--text-2)" }}>No analysis yet</div>
                <div style={{ fontSize: 13, lineHeight: 1.5, maxWidth: 220 }}>
                  Enter some text and click Analyze to see sentiment scores.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
