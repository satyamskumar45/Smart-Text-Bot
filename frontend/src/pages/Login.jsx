import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, status } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const redirectTo = location.state?.from?.pathname || "/dashboard";

  if (status !== "loading" && isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (submitting) {
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      await login(form);
      navigate(redirectTo, { replace: true });
    } catch (submitError) {
      setError(submitError.message || "Unable to log in.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-hero">
        <div className="auth-panel auth-panel-brand">
          <div className="hero-eyebrow">
            <span className="hero-eyebrow-dot" />
            Secure workspace access
          </div>
          <h1 className="auth-title">Welcome back to SmartTextBot</h1>
          <p className="auth-copy">
            Sign in to unlock your dashboard, saved activity, and the full language
            intelligence workspace.
          </p>
          <div className="auth-feature-list">
            <div className="auth-feature-item">JWT-backed session with `/auth/me` restore</div>
            <div className="auth-feature-item">Protected dashboard and tool routes</div>
            <div className="auth-feature-item">Persistent local session in this browser</div>
          </div>
        </div>

        <div className="auth-panel auth-panel-form">
          <div className="auth-form-header">
            <span className="auth-kicker">Login</span>
            <h2>Sign in</h2>
            <p>Use the same backend credentials served by your Flask auth routes.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="input-group">
              <label className="input-label" htmlFor="login-email">
                Email
              </label>
              <input
                id="login-email"
                name="email"
                type="email"
                value={form.email}
                onChange={updateField}
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label" htmlFor="login-password">
                Password
              </label>
              <input
                id="login-password"
                name="password"
                type="password"
                value={form.password}
                onChange={updateField}
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />
            </div>

            {error ? <div className="auth-error">{error}</div> : null}

            <button type="submit" className="btn btn-primary btn-full" disabled={submitting}>
              {submitting ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="auth-switch">
            New here? <Link to="/signup">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
