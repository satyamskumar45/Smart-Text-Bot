import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login, startGuest } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (event) => {
    event.preventDefault();
    if (loading) return;

    setLoading(true);
    setError(null);

    try {
      await login({ email, password, remember });
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message || "Unable to log in. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGuest = async () => {
    if (loading) return;

    setLoading(true);
    setError(null);
    try {
      await startGuest();
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message || "Unable to start guest mode.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <span>SmartTextBot</span>
          <p>Secure startup-grade access for your language intelligence workspace.</p>
        </div>

        <form onSubmit={handleLogin} className="auth-form">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            required
          />

          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your secure password"
            required
          />

          <div className="auth-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={remember}
                onChange={() => setRemember((prev) => !prev)}
              />
              Remember me
            </label>
            <Link className="secondary-link" to="/auth/signup">
              Create account
            </Link>
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" className="primary-button" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={handleGuest}
            disabled={loading}
          >
            Continue as guest
          </button>
        </form>

        <p className="auth-note">
          Guest mode includes limited daily credits; upgrade any time for unlimited access.
        </p>
      </div>
    </div>
  );
}
