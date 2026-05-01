import { useAuth } from "../context/AuthContext";

export default function AccountSettings() {
  const { user, logout } = useAuth();

  return (
    <div className="panel page-panel">
      <div className="panel-heading">
        <div>
          <h2>Account settings</h2>
          <p>Manage your profile, session persistence, and security settings.</p>
        </div>
      </div>

      <div className="settings-grid">
        <div className="account-card">
          <span className="label">Email</span>
          <strong>{user?.email || "guest@smarttextbot.local"}</strong>
        </div>
        <div className="account-card">
          <span className="label">Profile</span>
          <strong>{user?.display_name || "Guest Learner"}</strong>
        </div>
        <div className="account-card">
          <span className="label">Role</span>
          <strong>{user?.role}</strong>
        </div>
      </div>

      <div className="panel-actions">
        <button className="secondary-button" onClick={logout}>
          Sign out
        </button>
      </div>
    </div>
  );
}
