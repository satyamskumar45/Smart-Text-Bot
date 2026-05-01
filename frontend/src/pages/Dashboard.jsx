import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import * as api from "../services/api";

function StatCard({ label, value, note }) {
  return (
    <div className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
      {note && <small>{note}</small>}
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    api.fetchDashboard()
      .then((response) => setStats(response))
      .catch((err) => setError(err.message || "Unable to load dashboard."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <span className="eyebrow">Welcome back</span>
          <h1>{user?.display_name || "Learner"}</h1>
          <p className="subtext">
            Track translation usage, summaries, writing work, learning streaks, XP, favorites, and recent activity.
          </p>
        </div>
        <div className="upgrade-banner">
          <strong>{stats?.guest_mode ? "Guest mode" : "Signed in"}</strong>
          <span>
            {stats?.guest_mode
              ? "Your guest usage is being tracked, but long-term learning progress is limited."
              : "Your dashboard is showing real saved product activity."}
          </span>
        </div>
      </div>

      {loading && <div className="loading-card">Loading analytics...</div>}
      {error && <div className="status-error">{error}</div>}

      {stats && (
        <>
          <div className="grid cards-grid">
            <StatCard label="Total translations" value={stats.summary.total_translations} />
            <StatCard label="Saved summaries" value={stats.summary.saved_summaries} />
            <StatCard label="Writing sessions" value={stats.summary.writing_improvements} />
            <StatCard label="Learning streak" value={stats.summary.learning_streak} note={`Best: ${stats.summary.best_streak}`} />
            <StatCard label="XP progress" value={stats.summary.xp} note={`Level ${stats.summary.level}`} />
            <StatCard label="Quiz completions" value={stats.summary.completed_quizzes} />
            <StatCard label="Vocabulary mastered" value={stats.summary.vocabulary_mastered} />
            <StatCard label="Favorite items" value={stats.summary.favorites_count} />
          </div>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <h2>Recent activity</h2>
                <p>Every major tool writes here so the dashboard reflects real work, not placeholder UI.</p>
              </div>
            </div>

            <div className="activity-list">
              {stats.recent_activity.length ? (
                stats.recent_activity.map((item) => (
                  <article key={item.id} className="activity-card">
                    <div className="activity-meta">
                      <span>{item.module_type}</span>
                      <small>{new Date(item.created_at).toLocaleString()}</small>
                    </div>
                    <div className="activity-content">
                      <p>{item.input_text?.slice(0, 120) || "-"}</p>
                      <pre>{item.output_text?.slice(0, 180) || "-"}</pre>
                    </div>
                  </article>
                ))
              ) : (
                <div className="empty-state">No activity yet. Start with translation, summarization, writing, or learning.</div>
              )}
            </div>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <h2>Favorites</h2>
                <p>Your pinned outputs and learning items.</p>
              </div>
            </div>
            <div className="history-grid">
              {stats.favorites.length ? (
                stats.favorites.map((item) => (
                  <article key={item.id} className="history-card">
                    <header>
                      <span>{item.module_type}</span>
                      <small>{new Date(item.created_at).toLocaleDateString()}</small>
                    </header>
                    <div className="history-body">
                      <p>{item.output_text?.slice(0, 220) || "-"}</p>
                    </div>
                  </article>
                ))
              ) : (
                <div className="empty-state">No favorites saved yet.</div>
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
