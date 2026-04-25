import { useState } from "react";
import { BrowserRouter, Routes, Route, NavLink, useLocation } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import Favorites from "./pages/Favorites";
import AccountSettings from "./pages/AccountSettings";
import Translate from "./pages/Translate";
import Sentiment from "./pages/Sentiment";
import Summarizer from "./pages/Summarizer";
import Pipeline from "./pages/Pipeline";
import WritingAssistant from "./pages/WritingAssistant";
import Chat from "./pages/Chat";
import ContextEngine from "./pages/ContextEngine";
import NotFound from "./pages/NotFound";
import "./style.css";

const navItems = [
  { to: "/", icon: "DB", label: "Dashboard", exact: true },
  { to: "/translate", icon: "TR", label: "Translator" },
  { to: "/summarize", icon: "SU", label: "Summarizer" },
  { to: "/writing", icon: "WR", label: "Writing" },
  { to: "/learning", icon: "LE", label: "Learning" },
  { to: "/context", icon: "CX", label: "Context Engine" },
  { to: "/pipeline", icon: "DP", label: "Doc Pipeline" },
  { to: "/history", icon: "HI", label: "History" },
  { to: "/favorites", icon: "FV", label: "Favorites" },
  { to: "/settings", icon: "AC", label: "Account" },
];

const pageTitles = {
  "/": "Dashboard",
  "/translate": "Smart Translator",
  "/context": "Context Engine",
  "/pipeline": "Document Pipeline",
  "/writing": "Writing Assistant",
  "/chat": "Smart Learning Assistant",
  "/learning": "Smart Learning Assistant",
  "/sentiment": "Sentiment Analysis",
  "/summarize": "Text Summarizer",
  "/history": "History",
  "/favorites": "Favorites",
  "/settings": "Account Settings",
  "/auth/login": "Sign in",
  "/auth/signup": "Sign up",
};

function Sidebar({ isOpen, onClose }) {
  const location = useLocation();
  if (location.pathname.startsWith("/auth")) {
    return null;
  }

  return (
    <aside className={`sidebar${isOpen ? " open" : ""}`}>
      <div className="sidebar-logo">
        <div className="sidebar-logo-mark">
          <div className="logo-icon">ST</div>
          <span className="logo-name">SmartTextBot</span>
        </div>
        <button type="button" className="sidebar-close" onClick={onClose} aria-label="Close navigation">
          ×
        </button>
      </div>
      <div className="logo-tagline">Translation, writing, learning, and document intelligence</div>

      <nav className="sidebar-nav">
        <div className="nav-label">Navigation</div>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.exact}
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
            onClick={onClose}
          >
            <div className="nav-icon">{item.icon}</div>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-badge">
          <div className="status-dot" />
          <span className="status-text">Secure auth and persistent product data</span>
        </div>
      </div>
    </aside>
  );
}

function Topbar({ onMenuClick }) {
  const location = useLocation();
  const title = pageTitles[location.pathname] || "SmartTextBot";
  if (location.pathname.startsWith("/auth")) {
    return null;
  }

  return (
    <header className="topbar">
      <button className="menu-button" onClick={onMenuClick} aria-label="Open navigation">
        ☰
      </button>
      <span className="topbar-title">{title}</span>
      <div className="topbar-meta">
        <span className="model-badge">Production workspace</span>
        <span>·</span>
        <span>Connected SaaS features</span>
      </div>
    </header>
  );
}

function ProtectedPage({ children }) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const closeSidebar = () => setSidebarOpen(false);
  const toggleSidebar = () => setSidebarOpen((current) => !current);

  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="app-shell">
          <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
          <div className={`sidebar-backdrop${sidebarOpen ? " active" : ""}`} onClick={closeSidebar} />
          <div className="main-content">
            <Topbar onMenuClick={toggleSidebar} />
            <div className="page-content">
              <Routes>
                <Route path="/auth/login" element={<Login />} />
                <Route path="/auth/signup" element={<Signup />} />

                <Route path="/" element={<ProtectedPage><Dashboard /></ProtectedPage>} />
                <Route path="/translate" element={<ProtectedPage><Translate /></ProtectedPage>} />
                <Route path="/context" element={<ProtectedPage><ContextEngine /></ProtectedPage>} />
                <Route path="/pipeline" element={<ProtectedPage><Pipeline /></ProtectedPage>} />
                <Route path="/writing" element={<ProtectedPage><WritingAssistant /></ProtectedPage>} />
                <Route path="/learning" element={<ProtectedPage><Chat /></ProtectedPage>} />
                <Route path="/chat" element={<ProtectedPage><Chat /></ProtectedPage>} />
                <Route path="/sentiment" element={<ProtectedPage><Sentiment /></ProtectedPage>} />
                <Route path="/summarize" element={<ProtectedPage><Summarizer /></ProtectedPage>} />
                <Route path="/history" element={<ProtectedPage><History /></ProtectedPage>} />
                <Route path="/favorites" element={<ProtectedPage><Favorites /></ProtectedPage>} />
                <Route path="/settings" element={<ProtectedPage><AccountSettings /></ProtectedPage>} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
          </div>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
