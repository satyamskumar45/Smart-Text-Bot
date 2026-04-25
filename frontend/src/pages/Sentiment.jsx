import { useState } from "react";
import { sentiment } from "../services/api";

const VERDICTS = {
  positive: { emoji: "😊", label: "Positive", color: "#4cde9c" },
  negative: { emoji: "😞", label: "Negative", color: "#ff5b6a" },
  neutral: { emoji: "😐", label: "Neutral", color: "#4f8ef7" },
};

export default function Sentiment() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await sentiment(text);

      // Data should have: sentiment, positive, negative, neutral, explanation
      const percentages = {
        positive: Math.round((data.positive || 0) * 100),
        negative: Math.round((data.negative || 0) * 100),
        neutral: Math.round((data.neutral || 0) * 100),
      };

      setResult({
        ...percentages,
        verdict: data.sentiment || "neutral",
        explanation: data.explanation || "",
      });
    } catch (err) {
      console.error("[SENTIMENT ERROR]", err);
      setError(err.message || "Failed to analyze sentiment");
      setResult(null);
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
    <div>
      <div className="page-header">
        <h1>Sentiment Analysis</h1>
        <p>Analyze the emotional tone of any text with AI-powered sentiment scoring.</p>
      </div>

      {/* Error Banner */}
      {error && (
        <div
          style={{
            padding: "12px 16px",
            backgroundColor: "#ff5b6a22",
            borderLeft: "3px solid #ff5b6a",
            marginBottom: "16px",
            borderRadius: "6px",
            fontSize: "13px",
            color: "#ff5b6a",
          }}
        >
          ⚠ {error}
          <button
            onClick={() => setError(null)}
            style={{
              float: "right",
              background: "none",
              border: "none",
              cursor: "pointer",
              fontSize: "16px",
            }}
          >
            ✕
          </button>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <span className="card-title-icon">◉</span>
            Sentiment Analyzer
          </div>
          {result && verdict && (
            <div className="badge-live">
              <span className="dot" /> Result Ready
            </div>
          )}
        </div>

        <div className="sentiment-layout">
          {/* Input Pane */}
          <div className="sentiment-input-pane">
            <div>
              <label className="input-label">Text to Analyze</label>
              <textarea
                className="textarea-main"
                style={{ height: 180 }}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste or type any text — a review, tweet, message, or article…"
              />
            </div>

            <button
              className="btn btn-primary btn-full"
              onClick={run}
              disabled={loading || !text.trim()}
            >
              {loading ? (
                <>
                  <div className="spinner" /> Analyzing…
                </>
              ) : (
                <>◉ Analyze Sentiment</>
              )}
            </button>

            <div style={{ fontSize: 12, color: "var(--text-3)", lineHeight: 1.5 }}>
              The model classifies text as positive, negative, or neutral and returns a confidence
              score for each category.
            </div>
          </div>

          {/* Divider */}
          <div className="sentiment-divider" />

          {/* Result Pane */}
          <div className="sentiment-result-pane">
            <div className="result-header">Analysis Results</div>

            {result && verdict ? (
              <>
                <div className="sentiment-verdict" style={{ borderColor: `${verdict.color}30` }}>
                  <div className="verdict-emoji">{verdict.emoji}</div>
                  <div>
                    <div className="verdict-label" style={{ color: verdict.color }}>
                      {verdict.label}
                    </div>
                    <div className="verdict-score">
                      Overall sentiment · {result[result.verdict]}% confidence
                    </div>
                  </div>
                </div>

                <div className="sentiment-bar-group">
                  {bars.map((b) => (
                    <div key={b.key} className="sentiment-bar-item">
                      <div className="bar-meta">
                        <div className="bar-label">
                          <div className="bar-dot" style={{ background: b.dot }} />
                          {b.label}
                        </div>
                        <div className="bar-pct">{result[b.key]}%</div>
                      </div>
                      <div className="progress-track">
                        <div
                          className={`progress-fill ${b.cls}`}
                          style={{ width: `${result[b.key]}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {result.explanation && (
                  <div
                    style={{
                      marginTop: 16,
                      padding: "12px 14px",
                      backgroundColor: "var(--surface-2)",
                      borderRadius: "6px",
                      fontSize: "13px",
                      color: "var(--text-2)",
                      lineHeight: 1.6,
                    }}
                  >
                    <strong>Explanation:</strong> {result.explanation}
                  </div>
                )}
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
                <div style={{ fontSize: 32, opacity: 0.3 }}>◉</div>
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
