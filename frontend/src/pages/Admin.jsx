import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import * as api from "../services/api";

const adminCards = [
  { key: "total_users", label: "Total Users" },
  { key: "total_history_entries", label: "History Entries" },
  { key: "total_active_sessions", label: "Active Sessions" },
  { key: "total_guest_sessions", label: "Guest Sessions" },
];

function StatCard({ label, value }) {
  return (
    <article className="dashboard-stat-card">
      <span>{label}</span>
      <strong>{value ?? 0}</strong>
    </article>
  );
}

export default function Admin() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [search, setSearch] = useState("");
  const [busyUserId, setBusyUserId] = useState("");

  useEffect(() => {
    let ignore = false;

    async function loadAdminData() {
      setLoading(true);
      setError("");

      try {
        const [statsResponse, usersResponse] = await Promise.all([
          api.fetchAdminStats(),
          api.fetchAdminUsers(),
        ]);

        if (ignore) {
          return;
        }

        setStats(statsResponse.stats || {});
        setUsers(usersResponse.users || []);
      } catch (loadError) {
        if (!ignore) {
          setError(loadError.message || "Unable to load admin data.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    loadAdminData();

    return () => {
      ignore = true;
    };
  }, []);

  const filteredUsers = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) {
      return users;
    }

    return users.filter((entry) => {
      return (
        entry.email?.toLowerCase().includes(query) ||
        entry.role?.toLowerCase().includes(query)
      );
    });
  }, [search, users]);

  async function handleRoleChange(userId, nextRole) {
    setBusyUserId(userId);
    setError("");
    setNotice("");

    try {
      const response = await api.updateAdminUserRole(userId, nextRole);
      setUsers((current) =>
        current.map((entry) => (entry.id === userId ? { ...entry, ...response.user } : entry))
      );
      setNotice("User role updated successfully.");
    } catch (updateError) {
      setError(updateError.message || "Unable to update user role.");
    } finally {
      setBusyUserId("");
    }
  }

  async function handleDelete(userId, email) {
    const confirmed = window.confirm(`Delete ${email}? This will remove related user data.`);
    if (!confirmed) {
      return;
    }

    setBusyUserId(userId);
    setError("");
    setNotice("");

    try {
      await api.deleteAdminUser(userId);
      setUsers((current) => current.filter((entry) => entry.id !== userId));
      setStats((current) =>
        current
          ? {
              ...current,
              total_users: Math.max((current.total_users || 1) - 1, 0),
            }
          : current
      );
      setNotice("User deleted successfully.");
    } catch (deleteError) {
      setError(deleteError.message || "Unable to delete user.");
    } finally {
      setBusyUserId("");
    }
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1>Admin Dashboard</h1>
        <p>Restricted analytics and user management for administrators.</p>
      </div>

      {loading ? <div className="loading-card">Loading admin dashboard...</div> : null}
      {error ? <div className="auth-error">{error}</div> : null}
      {notice ? <div className="admin-notice">{notice}</div> : null}

      {stats && !loading ? (
        <div className="dashboard-grid">
          {adminCards.map((card) => (
            <StatCard key={card.key} label={card.label} value={stats[card.key]} />
          ))}
        </div>
      ) : null}

      <section className="admin-panel">
        <div className="admin-panel-header">
          <div>
            <h2>User Management</h2>
            <p>Search, promote, demote, or remove accounts.</p>
          </div>
          <input
            className="admin-search"
            type="text"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by email or role"
          />
        </div>

        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Role</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((entry) => {
                const isBusy = busyUserId === entry.id;
                const isCurrentAdmin = user?.id === entry.id;

                return (
                  <tr key={entry.id}>
                    <td>{entry.email}</td>
                    <td>
                      <select
                        className="admin-select"
                        value={entry.role}
                        onChange={(event) => handleRoleChange(entry.id, event.target.value)}
                        disabled={isBusy}
                      >
                        <option value="user">user</option>
                        <option value="admin">admin</option>
                      </select>
                    </td>
                    <td>{entry.created_at ? new Date(entry.created_at).toLocaleString() : "-"}</td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-ghost admin-danger-btn"
                        onClick={() => handleDelete(entry.id, entry.email)}
                        disabled={isBusy || isCurrentAdmin}
                        title={isCurrentAdmin ? "You cannot delete your own admin account." : "Delete user"}
                      >
                        {isBusy ? "Working..." : "Delete"}
                      </button>
                    </td>
                  </tr>
                );
              })}

              {!filteredUsers.length ? (
                <tr>
                  <td colSpan="4" className="admin-empty">
                    No users match this filter.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
