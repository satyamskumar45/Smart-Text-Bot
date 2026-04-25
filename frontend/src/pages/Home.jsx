import { Link } from "react-router-dom";

const features = [
  {
    to: "/translate",
    color: "teal",
    icon: "⇄",
    title: "Smart Translator",
    desc: "Multi-output translation — Simple, Professional, and Native styles — with AI explanation of meaning and tone.",
  },
  {
    to: "/context",
    color: "purple",
    icon: "🎨",
    title: "Context Engine",
    desc: "Transform any text to match the perfect tone: Formal, Professional, Academic, Casual, or Persuasive.",
  },
  {
    to: "/pipeline",
    color: "pink",
    icon: "▶",
    title: "Document Pipeline",
    desc: "Upload an image → extract text with OCR → translate to any language → generate a smart summary.",
  },
  {
    to: "/writing",
    color: "amber",
    icon: "✏️",
    title: "Writing Assistant",
    desc: "Fix grammar, improve tone, or fully rewrite your text for clarity and impact with AI suggestions.",
  },
  {
    to: "/chat",
    color: "teal",
    icon: "🎯",
    title: "Language Quest",
    desc: "Gamified language training with daily challenges, curated phrases, and translation practice.",
  },
  {
    to: "/sentiment",
    color: "blue",
    icon: "◉",
    title: "Sentiment Analysis",
    desc: "Analyze emotional tone with AI confidence scores — positive, negative, and neutral breakdown.",
  },
  {
    to: "/summarize",
    color: "green",
    icon: "📝",
    title: "Text Summarizer",
    desc: "Generate concise paragraph summaries and key bullet points from any long-form text instantly.",
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
        Language intelligence,<br />
        <span className="gradient-text">built for everyone</span>
      </h1>

      <p className="hero-sub">
        A unified AI platform for translation, summarization, writing assistance,
        and language analysis — powered by OpenAI.
      </p>

      <div className="feature-grid">
        {features.map((f) => (
          <Link key={f.to} to={f.to} className={`feature-card ${f.color}`}>
            <div className="feature-icon">{f.icon}</div>
            <div className="feature-title">{f.title}</div>
            <div className="feature-desc">{f.desc}</div>
            <div className="feature-arrow">→</div>
          </Link>
        ))}
      </div>

      <div className="stats-row">
        <div className="stat-item">
          <span className="stat-value">7</span>
          <span className="stat-label">AI Modules</span>
        </div>
        <div className="stat-divider" />
        <div className="stat-item">
          <span className="stat-value">100+</span>
          <span className="stat-label">Languages</span>
        </div>
        <div className="stat-divider" />
        <div className="stat-item">
          <span className="stat-value">5</span>
          <span className="stat-label">Tone Styles</span>
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
