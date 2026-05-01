import { useEffect, useState } from "react";
import * as api from "../services/api";

const statCards = [
  { key: "history_count", label: "History Items" },
  { key: "favorites_count", label: "Favorites" },
  { key: "translations_count", label: "Translations" },
  { key: "summaries_count", label: "Summaries" },
  { key: "chat_count", label: "Chats" },
  { key: "streak_count", label: "Current Streak" },
  { key: "modules_started", label: "Modules Started" },
  { key: "modules_completed", label: "Modules Completed" },
];

function StatCard({ label, value }) {
  return (
    <article className="dashboard-stat-card">
      <span>{label}</span>
      <strong>{value ?? 0}</strong>
    </article>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const response = await api.fetchDashboard();
        if (!ignore) {
          setStats(response.stats || {});
        }
      } catch (loadError) {
        if (!ignore) {
          setError(loadError.message || "Unable to load dashboard.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      ignore = true;
    };
  }, []);

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>
          Your authenticated workspace overview, powered by the existing backend
          dashboard endpoint.
        </p>
      </div>

      {loading ? <div className="loading-card">Loading dashboard metrics...</div> : null}
      {error ? <div className="auth-error">{error}</div> : null}

      {stats && !loading ? (
        <div className="dashboard-grid">
          {statCards.map((card) => (
            <StatCard key={card.key} label={card.label} value={stats[card.key]} />
          ))}
        </div>
      ) : null}
    </div>
  );
}
