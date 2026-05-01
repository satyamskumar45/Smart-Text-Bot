import { BrowserRouter, NavLink, Route, Routes, useLocation } from "react-router-dom";
import Chat from "./pages/Chat";
import Home from "./pages/Home";
import ImageScanner from "./pages/ImageScanner";
import Sentiment from "./pages/Sentiment";
import Summarizer from "./pages/Summarizer";
import Translate from "./pages/Translate";
import "./style.css";

const API_BASE_URL =
  (typeof process !== "undefined" && process.env?.REACT_APP_API_URL) ||
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL) ||
  "http://localhost:5000";

const navItems = [
  { to: "/", icon: "⌂", label: "Overview", exact: true },
  { to: "/chat", icon: "💬", label: "AI Chat" },
  { to: "/translate", icon: "⇄", label: "Translate" },
  { to: "/sentiment", icon: "●", label: "Sentiment" },
  { to: "/summarize", icon: "📝", label: "Summarizer" },
  { to: "/image-scan", icon: "🖼️", label: "Image Scanner" },
];

const pageTitles = {
  "/": "Dashboard",
  "/chat": "AI Chat",
  "/translate": "Translation",
  "/sentiment": "Sentiment Analysis",
  "/summarize": "Text Summarizer",
  "/image-scan": "Image Scanner",
};

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-mark">
          <div className="logo-icon">🤖</div>
          <span className="logo-name">SmartTextBot</span>
        </div>
        <div className="logo-tagline">v2.0 · AI Platform</div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-label">Navigation</div>
        {navItems.map((item) => (
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
  const title = pageTitles[location.pathname] || "SmartTextBot";

  return (
    <header className="topbar">
      <span className="topbar-title">{title}</span>
      <div className="topbar-meta">
        <span className="model-badge">API</span>
        <span>·</span>
        <span>{API_BASE_URL}</span>
      </div>
    </header>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar />
        <div className="main-content">
          <Topbar />
          <div className="page-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/translate" element={<Translate />} />
              <Route path="/sentiment" element={<Sentiment />} />
              <Route path="/summarize" element={<Summarizer />} />
              <Route path="/image-scan" element={<ImageScanner />} />
            </Routes>
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}
