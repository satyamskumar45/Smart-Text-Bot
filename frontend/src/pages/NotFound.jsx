import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <span>Page not found</span>
          <p>The page you are looking for does not exist.</p>
        </div>
        <Link className="primary-button" to="/">
          Return to dashboard
        </Link>
      </div>
    </div>
  );
}
