import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import * as api from "../services/api";

const statCards = [
  { key: "history_count", label: "Saved Work", accent: "teal" },
  { key: "translations_count", label: "Translations", accent: "blue" },
  { key: "summaries_count", label: "Summaries", accent: "amber" },
  { key: "chat_count", label: "Practice Sessions", accent: "teal" },
  { key: "streak_count", label: "Learning Streak", accent: "blue" },
  { key: "favorites_count", label: "Favorites", accent: "amber" },
];

const missions = [
  { title: "Translate one useful sentence", reward: "15 XP", path: "/translate" },
  { title: "Finish one Language Quest quiz", reward: "20 XP", path: "/chat" },
  { title: "Summarize a paragraph", reward: "10 XP", path: "/summarize" },
];

function StatCard({ item, value }) {
  return (
    <article className={`dashboard-stat-card stat-${item.accent}`}>
      <span>{item.label}</span>
      <strong>{value ?? 0}</strong>
    </article>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState({});
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

  const totalActivity = useMemo(
    () => statCards.reduce((sum, item) => sum + Number(stats[item.key] || 0), 0),
    [stats]
  );

  const completion = Math.min(100, Math.max(12, totalActivity * 8));

  return (
    <div className="dashboard-page dashboard-v2 motion-safe:animate-[fade-in_0.35s_ease]">
      <section className="dashboard-hero">
        <div>
          <div className="hero-eyebrow">
            <span className="hero-eyebrow-dot" />
            Today in SmartTextBot
          </div>
          <h1>Your AI language cockpit is ready.</h1>
          <p>Track practice, launch tools, and keep your learning streak moving with small daily wins.</p>
        </div>
        <div className="dashboard-level-card">
          <span>Daily momentum</span>
          <strong>{completion}%</strong>
          <div className="quest-progress">
            <div style={{ width: `${completion}%` }} />
          </div>
        </div>
      </section>

      {loading ? (
        <div className="loading-card flex items-center gap-3">
          <div className="spinner" /> Loading dashboard metrics...
        </div>
      ) : null}
      {error ? <div className="auth-error" role="alert">{error}</div> : null}

      <div className="dashboard-grid">
        {statCards.map((item) => (
          <StatCard key={item.key} item={item} value={stats[item.key]} />
        ))}
      </div>

      <div className="dashboard-panels">
        <section className="card">
          <div className="card-header">
            <div className="card-title">Daily Missions</div>
            <div className="badge-live"><span className="dot" />Active</div>
          </div>
          <div className="mission-list">
            {missions.map((mission) => (
              <Link key={mission.title} className="mission-item transition-all duration-200 hover:-translate-y-0.5" to={mission.path}>
                <span>{mission.title}</span>
                <strong>{mission.reward}</strong>
              </Link>
            ))}
          </div>
        </section>

        <section className="card">
          <div className="card-header">
            <div className="card-title">Recommended Flow</div>
            <div className="badge-live"><span className="dot" />3 steps</div>
          </div>
          <div className="flow-list">
            <div><strong>1</strong><span>Warm up in Language Quest</span></div>
            <div><strong>2</strong><span>Translate a real sentence</span></div>
            <div><strong>3</strong><span>Save the best output as a favorite</span></div>
          </div>
        </section>
      </div>
    </div>
  );
}
