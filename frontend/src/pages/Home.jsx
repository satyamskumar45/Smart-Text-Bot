import { Link } from "react-router-dom";

const features = [
  {
    to: "/chat",
    color: "teal",
    icon: "💬",
    title: "AI Chat",
    desc: "Natural language conversations powered by GPT. Ask anything, get intelligent answers in real time.",
  },
  {
    to: "/translate",
    color: "blue",
    icon: "⇄",
    title: "Translate",
    desc: "Instant translation between 100+ languages with voice input support and one-click copy.",
  },
  {
    to: "/sentiment",
    color: "amber",
    icon: "●",
    title: "Sentiment Analysis",
    desc: "Analyze tone and emotion in any text. Get positive, negative, and neutral confidence scores.",
  },
  {
    to: "/summarize",
    color: "purple",
    icon: "📝",
    title: "Text Summarizer",
    desc: "Generate concise summaries from long text using AI in seconds.",
  },
  {
    to: "/image-scan",
    color: "pink",
    icon: "🖼️",
    title: "Image Scanner",
    desc: "Extract text and insights from images using OCR and AI.",
  },
  {
    to: "/pipeline",
    color: "teal",
    icon: "DP",
    title: "Document Pipeline",
    desc: "Upload an image, extract text, translate it, and generate a summary in one flow.",
  },
];

export default function Home() {
  return (
    <div className="home-hero">
      <div className="hero-eyebrow">
        <span className="hero-eyebrow-dot" />
        SmartTextBot AI Platform
      </div>

      <h1 className="hero-title">
        Language intelligence,
        <br />
        <span className="gradient-text">built for developers</span>
      </h1>

      <p className="hero-sub">
        A unified AI toolkit for chat, translation, and sentiment analysis.
        Connect your backend and start processing language in seconds.
      </p>

      <div className="feature-grid">
        {features.map((feature) => (
          <Link key={feature.to} to={feature.to} className={`feature-card ${feature.color}`}>
            <div className="feature-icon">{feature.icon}</div>
            <div className="feature-title">{feature.title}</div>
            <div className="feature-desc">{feature.desc}</div>
            <div className="feature-arrow">→</div>
          </Link>
        ))}
      </div>

      <div className="stats-row">
        <div className="stat-item">
          <span className="stat-value">3</span>
          <span className="stat-label">AI Modules</span>
        </div>
        <div className="stat-divider" />
        <div className="stat-item">
          <span className="stat-value">100+</span>
          <span className="stat-label">Languages</span>
        </div>
        <div className="stat-divider" />
        <div className="stat-item">
          <span className="stat-value">~100ms</span>
          <span className="stat-label">Avg. Latency</span>
        </div>
        <div className="stat-divider" />
        <div className="stat-item">
          <span className="stat-value">REST</span>
          <span className="stat-label">API Backend</span>
        </div>
      </div>
    </div>
  );
}
