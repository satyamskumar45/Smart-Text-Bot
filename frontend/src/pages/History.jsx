import { useEffect, useState } from "react";
import * as api from "../services/api";

function formatTitle(item) {
  const map = {
    translation: "Translation",
    summary: "Summary",
    writing_assistant: "Writing Assistant",
    context_engine: "Context Engine",
    learning_assistant: "Learning Assistant",
  };
  return map[item.module_type] || item.module_type;
}

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.fetchHistory()
      .then((response) => setHistory(response.items || []))
      .catch((err) => setError(err.message || "Could not load history."))
      .finally(() => setLoading(false));
  }, []);

  const handleFavorite = async (item) => {
    try {
      await api.toggleFavorite(item.id, !item.favorite);
      setHistory((current) =>
        current.map((entry) => (entry.id === item.id ? { ...entry, favorite: !entry.favorite } : entry))
      );
    } catch (err) {
      setError(err.message || "Could not update favorite.");
    }
  };

  return (
    <div className="panel page-panel">
      <div className="panel-heading">
        <div>
          <h2>History</h2>
          <p>Saved translations, summaries, writing sessions, context transformations, and learning activity.</p>
        </div>
      </div>

      {loading && <div className="loading-card">Loading history...</div>}
      {error && <div className="status-error">{error}</div>}

      {!loading && !history.length && (
        <div className="empty-state">No saved items yet. Use the platform to build your activity history.</div>
      )}

      <div className="history-grid">
        {history.map((item) => (
          <article key={item.id} className="history-card">
            <header>
              <span>{formatTitle(item)}</span>
              <small>{new Date(item.created_at).toLocaleString()}</small>
            </header>
            <div className="history-body">
              <strong>Input</strong>
              <p>{item.input_text?.slice(0, 160) || "-"}</p>
              <strong>Output</strong>
              <p>{item.output_text?.slice(0, 260) || "-"}</p>
              {item.metadata?.language && (
                <p style={{ color: "var(--text-3)", fontSize: 12 }}>
                  Language: {item.metadata.language.toUpperCase()} · Activity: {item.metadata.activity_type || "session"}
                </p>
              )}
            </div>
            <div className="action-row">
              <button className="btn btn-ghost" onClick={() => handleFavorite(item)}>
                {item.favorite ? "Unfavorite" : "Favorite"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
