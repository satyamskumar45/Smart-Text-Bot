import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const navigate = useNavigate();
  const { signup } = useAuth();
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSignup = async (event) => {
    event.preventDefault();
    if (loading) return;

    setLoading(true);
    setError(null);

    try {
      await signup({ email, password, display_name: displayName, remember });
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message || "Unable to create account.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <span>SmartTextBot</span>
          <p>Create a secure account and keep your learning history in one place.</p>
        </div>

        <form onSubmit={handleSignup} className="auth-form">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            required
          />

          <label>Display name</label>
          <input
            type="text"
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
            placeholder="Your name or alias"
          />

          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Create a strong password"
            required
          />

          <div className="auth-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={remember}
                onChange={() => setRemember((prev) => !prev)}
              />
              Keep me signed in
            </label>
            <Link className="secondary-link" to="/auth/login">
              Already have an account?
            </Link>
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" className="primary-button" disabled={loading}>
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="auth-note">
          Accounts include protected history, favorites, and seamless guest conversion.
        </p>
      </div>
    </div>
  );
}
