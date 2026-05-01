import { useState } from "react";
import { summarizeText } from "../services/api";

export default function Summarizer() {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");

  const handleSummarize = async () => {
    const data = await summarizeText(text);
    setSummary(data.summary);
  };

  return (
    <div className="page">
      <h1>Text Summarizer</h1>
      <p className="page-sub">Generate concise summaries using AI-powered language models.</p>

      <div className="tool-card">
        <div className="tool-header">
          <span>📝 Text Summarization</span>
          <span className="live-badge">● Live</span>
        </div>

        <div className="tool-body split">
          <div className="tool-section">
            <div className="section-label">INPUT</div>
            <textarea placeholder="Paste your text here..." value={text} onChange={(event) => setText(event.target.value)} />
          </div>

          <div className="tool-section">
            <div className="section-label">SUMMARY</div>
            <div className="output-box">{summary || "Summary will appear here..."}</div>
          </div>
        </div>

        <button onClick={handleSummarize} className="primary-btn">
          Summarize
        </button>
      </div>
    </div>
  );
}
