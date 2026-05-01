import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const navigate = useNavigate();
  const { signup, isAuthenticated, status } = useAuth();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (status !== "loading" && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
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

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      await signup({
        name: form.name.trim() || undefined,
        email: form.email,
        password: form.password,
      });
      navigate("/dashboard", { replace: true });
    } catch (submitError) {
      setError(submitError.message || "Unable to create account.");
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
            SmartTextBot onboarding
          </div>
          <h1 className="auth-title">Create your workspace account</h1>
          <p className="auth-copy">
            Register through the existing Flask backend and jump straight into your
            protected dashboard with a stored JWT session.
          </p>
          <div className="auth-feature-list">
            <div className="auth-feature-item">Connected to `POST /auth/signup`</div>
            <div className="auth-feature-item">Automatic login after account creation</div>
            <div className="auth-feature-item">Ready for protected routes and logout</div>
          </div>
        </div>

        <div className="auth-panel auth-panel-form">
          <div className="auth-form-header">
            <span className="auth-kicker">Signup</span>
            <h2>Create account</h2>
            <p>Passwords should follow the backend policy enforced by your API.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="input-group">
              <label className="input-label" htmlFor="signup-name">
                Name
              </label>
              <input
                id="signup-name"
                name="name"
                type="text"
                value={form.name}
                onChange={updateField}
                placeholder="Your display name"
              />
            </div>

            <div className="input-group">
              <label className="input-label" htmlFor="signup-email">
                Email
              </label>
              <input
                id="signup-email"
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
              <label className="input-label" htmlFor="signup-password">
                Password
              </label>
              <input
                id="signup-password"
                name="password"
                type="password"
                value={form.password}
                onChange={updateField}
                placeholder="Create a strong password"
                autoComplete="new-password"
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label" htmlFor="signup-confirm-password">
                Confirm password
              </label>
              <input
                id="signup-confirm-password"
                name="confirmPassword"
                type="password"
                value={form.confirmPassword}
                onChange={updateField}
                placeholder="Repeat your password"
                autoComplete="new-password"
                required
              />
            </div>

            {error ? <div className="auth-error">{error}</div> : null}

            <button type="submit" className="btn btn-primary btn-full" disabled={submitting}>
              {submitting ? "Creating account..." : "Create account"}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
