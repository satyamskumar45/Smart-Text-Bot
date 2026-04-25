import { useEffect, useState } from "react";
import * as api from "../services/api";

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadFavorites = () => {
    setLoading(true);
    api.fetchFavorites()
      .then((response) => setFavorites(response.items || []))
      .catch((err) => setError(err.message || "Unable to load favorites."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadFavorites();
  }, []);

  const removeFavorite = async (item) => {
    try {
      await api.toggleFavorite(item.id, false);
      setFavorites((current) => current.filter((entry) => entry.id !== item.id));
    } catch (err) {
      setError(err.message || "Unable to update favorite.");
    }
  };

  return (
    <div className="panel page-panel">
      <div className="panel-heading">
        <div>
          <h2>Favorites</h2>
          <p>Your saved outputs and learning sessions for fast review and reuse.</p>
        </div>
        <button className="btn btn-ghost" onClick={loadFavorites}>Refresh</button>
      </div>

      {loading && <div className="loading-card">Loading favorites...</div>}
      {error && <div className="status-error">{error}</div>}

      {!loading && !favorites.length && (
        <div className="empty-state">No favorites yet. Save any result from history or the main tools.</div>
      )}

      <div className="history-grid">
        {favorites.map((item) => (
          <article key={item.id} className="history-card">
            <header>
              <span>{item.module_type}</span>
              <small>{new Date(item.created_at).toLocaleString()}</small>
            </header>
            <div className="history-body">
              <strong>Input</strong>
              <p>{item.input_text?.slice(0, 160) || "-"}</p>
              <strong>Output</strong>
              <p>{item.output_text?.slice(0, 240) || "-"}</p>
            </div>
            <div className="action-row">
              <button className="btn btn-ghost" onClick={() => removeFavorite(item)}>Remove Favorite</button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
