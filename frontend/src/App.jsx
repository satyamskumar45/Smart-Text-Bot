import { BrowserRouter, Navigate, NavLink, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Admin from "./pages/Admin";
import Chat from "./pages/Chat";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import ImageScanner from "./pages/ImageScanner";
import Login from "./pages/Login";
import Sentiment from "./pages/Sentiment";
import Signup from "./pages/Signup";
import Summarizer from "./pages/Summarizer";
import Translate from "./pages/Translate";
import "./style.css";

const API_BASE_URL =
  (typeof process !== "undefined" && process.env?.REACT_APP_API_URL) ||
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL) ||
  "http://localhost:5000";

const navItems = [
  { to: "/dashboard", icon: "D", label: "Dashboard" },
  { to: "/", icon: "O", label: "Overview", exact: true },
  { to: "/chat", icon: "C", label: "AI Chat" },
  { to: "/translate", icon: "T", label: "Translate" },
  { to: "/sentiment", icon: "S", label: "Sentiment" },
  { to: "/summarize", icon: "M", label: "Summarizer" },
  { to: "/image-scan", icon: "I", label: "Image Scanner" },
  { to: "/admin", icon: "A", label: "Admin", role: "admin" },
];

const pageTitles = {
  "/": "Overview",
  "/dashboard": "Dashboard",
  "/chat": "AI Chat",
  "/translate": "Translation",
  "/sentiment": "Sentiment Analysis",
  "/summarize": "Text Summarizer",
  "/image-scan": "Image Scanner",
  "/admin": "Admin",
  "/login": "Login",
  "/signup": "Signup",
};

function Sidebar() {
  const { user } = useAuth();
  const visibleNavItems = navItems.filter((item) => !item.role || user?.role === item.role);

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-mark">
          <div className="logo-icon">AI</div>
          <span className="logo-name">SmartTextBot</span>
        </div>
        <div className="logo-tagline">v2.0 - AI Platform</div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-label">Navigation</div>
        {visibleNavItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.exact}
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
          >
            <div className="nav-icon">{item.icon}</div>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-badge">
          <div className="status-dot" />
          <span className="status-text">
            API <span>Connected</span>
          </span>
        </div>
      </div>
    </aside>
  );
}

function Topbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const title = pageTitles[location.pathname] || "SmartTextBot";

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="topbar">
      <div>
        <span className="topbar-title">{title}</span>
        <div className="topbar-meta">
          <span className="model-badge">API</span>
          <span>{API_BASE_URL}</span>
        </div>
      </div>

      <div className="topbar-actions">
        <div className="topbar-user">
          <span className="topbar-user-name">{user?.name || user?.email || "Authenticated User"}</span>
          <span className="topbar-user-role">{user?.role || "user"} · {user?.email}</span>
        </div>
        <button type="button" className="btn btn-ghost" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}

function PublicOnlyRoute({ children }) {
  const { isAuthenticated, status } = useAuth();

  if (status === "loading") {
    return <div className="page-loading">Loading authentication...</div>;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

function ProtectedAppLayout() {
  return (
    <ProtectedRoute>
      <div className="app-shell">
        <Sidebar />
        <div className="main-content">
          <Topbar />
          <div className="page-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/translate" element={<Translate />} />
              <Route path="/sentiment" element={<Sentiment />} />
              <Route path="/summarize" element={<Summarizer />} />
              <Route path="/image-scan" element={<ImageScanner />} />
              <Route
                path="/admin"
                element={
                  <ProtectedRoute role="admin">
                    <Admin />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <Login />
          </PublicOnlyRoute>
        }
      />
      <Route
        path="/signup"
        element={
          <PublicOnlyRoute>
            <Signup />
          </PublicOnlyRoute>
        }
      />
      <Route path="/*" element={<ProtectedAppLayout />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
