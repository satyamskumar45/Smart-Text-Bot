import { useState } from "react";
import { translate, explainTranslation } from "../services/api";
import LANGUAGES from "../data/languages";


const OUTPUT_CARDS = [
  { key: "simple", icon: "💬", label: "Simple", desc: "Plain, easy-to-understand" },
  { key: "professional", icon: "💼", label: "Professional", desc: "Formal & business-ready" },
  { key: "native", icon: "🌍", label: "Native", desc: "Natural, idiomatic phrasing" },
];

export default function Translate() {
  const [sourceLang, setSourceLang] = useState("en");
  const [targetLang, setTargetLang] = useState("hi");
  const [input, setInput] = useState("");
  const [outputs, setOutputs] = useState({});
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(null);
  const [translationDetails, setTranslationDetails] = useState(null);
  const [explanation, setExplanation] = useState("");
  const [explaining, setExplaining] = useState(false);
  const [activeExplain, setActiveExplain] = useState(null);
  const HISTORY_KEY = "smartTranslatorHistory";
  const [error, setError] = useState("");
  const [recentTranslations, setRecentTranslations] = useState(() => {
    try {
      const saved = localStorage.getItem(HISTORY_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const saveTranslationRecord = (record) => {
    const next = [record, ...recentTranslations].slice(0, 6);
    setRecentTranslations(next);
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
    } catch (err) {
      console.warn("Unable to save translation history", err);
    }
  };

  const run = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setOutputs({});
    setExplanation("");
    setActiveExplain(null);
    setError("");

    try {
      const responseData = await translate(input, sourceLang, targetLang);
      console.log("[DEBUG] API response:", responseData);

      // ✅ FIX: Backend returns { translated_text: "..." }
      // Map it into the three card format the UI expects.
      if (responseData.translated_text) {
        const translatedText = responseData.translated_text;
        setOutputs({
          simple: translatedText,
          professional: translatedText,
          native: translatedText,
        });
        setTranslationDetails(null);
        saveTranslationRecord({
          source: input,
          translated: translatedText,
          sourceLang,
          targetLang,
          createdAt: new Date().toISOString(),
        });
        await fetchTranslationDetails(translatedText);
      }
      // If backend already returns { simple, professional, native } (future-proof)
      else if (responseData.simple || responseData.professional || responseData.native) {
        setOutputs(responseData);
      }
      // Handle unexpected response shape
      else {
        console.error("[DEBUG] Unexpected response shape:", responseData);
        setError("Unexpected response from server. Check backend.");
      }
    } catch (err) {
      console.error("[DEBUG] Translation error:", err);
      const msg =
        err?.response?.data?.error ||
        "Translation failed. Is the backend running?";
      setError(msg);
      setOutputs({});
    } finally {
      setLoading(false);
    }
  };

  const copy = async (text, key) => {
    if (!text) return;
    await navigator.clipboard.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(null), 1500);
  };

  const fetchTranslationDetails = async (translationText) => {
    if (!translationText || !input.trim()) return;
    setExplaining(true);
    setTranslationDetails(null);
    try {
      const detail = await explainTranslation(input, translationText, sourceLang, targetLang);
      setTranslationDetails(detail || null);
      setExplanation(detail?.meaning || "");
    } catch {
      setExplanation("Could not generate translation learning details.");
      setTranslationDetails(null);
    } finally {
      setExplaining(false);
    }
  };

  const explain = async (translationText, cardKey) => {
    if (!translationText || !input.trim()) return;
    setActiveExplain(cardKey);
    setExplaining(true);
    setExplanation("");
    try {
      const detail = await explainTranslation(input, translationText, sourceLang, targetLang);
      setTranslationDetails(detail || null);
      setExplanation(detail?.meaning || detail?.simple || "");
    } catch {
      setExplanation("Could not generate explanation.");
      setTranslationDetails(null);
    } finally {
      setExplaining(false);
    }
  };

  const hasResults = outputs.simple || outputs.professional || outputs.native;

  return (
    <div className="translate-layout">
      <div className="page-header">
        <h1>Smart Translator</h1>
        <p>Multi-output translation — Simple, Professional, and Native styles — powered by AI.</p>
      </div>

      {/* Input Card */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <span className="card-title-icon">⇄</span>
            Translation Input
          </div>
          <div className="badge-live"><span className="dot" />Live</div>
        </div>

        {/* Language Row */}
        <div className="lang-row">
          <select
            className="lang-select lang-select-dropdown"
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value)}
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>{l.name}</option>
            ))}
          </select>
          <button
            className="swap-btn"
            title="Swap languages"
            onClick={() => { setSourceLang(targetLang); setTargetLang(sourceLang); }}
          >⇄</button>
          <select
            className="lang-select lang-select-dropdown"
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>{l.name}</option>
            ))}
          </select>
        </div>

        {/* Source Text */}
        <div className="dual-pane-label" style={{ background: "var(--bg-3)", borderRadius: "var(--radius-sm) var(--radius-sm) 0 0", borderBottom: "1px solid var(--border)" }}>
          Source Text
        </div>
        <textarea
          className="textarea-main"
          style={{ borderTopLeftRadius: 0, borderTopRightRadius: 0, marginBottom: 16 }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter text to translate…"
        />

        <div className="action-row">
          <div className="spacer" />
          <button
            className="btn btn-primary"
            onClick={run}
            disabled={loading || !input.trim()}
          >
            {loading ? <><div className="spinner" /> Translating…</> : <>⇄ Translate</>}
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="card" style={{ borderColor: "var(--error, #e53e3e)", background: "var(--error-bg, #fff5f5)" }}>
          <p style={{ color: "var(--error, #e53e3e)", margin: 0 }}>⚠️ {error}</p>
        </div>
      )}

      {/* Output Cards */}
      {(hasResults || loading) && (
        <div className="translate-outputs-grid">
          {OUTPUT_CARDS.map((card) => (
            <div key={card.key} className="translate-output-card">
              <div className="toc-header">
                <span className="toc-icon">{card.icon}</span>
                <div>
                  <div className="toc-label">{card.label}</div>
                  <div className="toc-desc">{card.desc}</div>
                </div>
                {outputs[card.key] && (
                  <button
                    className="btn btn-ghost btn-icon toc-copy"
                    onClick={() => copy(outputs[card.key], card.key)}
                    title="Copy"
                  >{copied === card.key ? "✓" : "⎘"}</button>
                )}
              </div>
              <div className="toc-body">
                {loading
                  ? <div className="toc-placeholder"><div className="skeleton-line" /><div className="skeleton-line short" /></div>
                  : <p>{outputs[card.key] || "—"}</p>
                }
              </div>
              {outputs[card.key] && (
                <button
                  className="btn btn-ghost toc-explain-btn"
                  onClick={() => explain(outputs[card.key], card.key)}
                  disabled={explaining && activeExplain === card.key}
                >
                  {explaining && activeExplain === card.key
                    ? <><div className="spinner" style={{ borderTopColor: "var(--text-3)" }} /> Explaining…</>
                    : <>💡 Explain Translation</>
                  }
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Explanation Panel */}
      {((translationDetails && !explaining) || (explanation && (explaining || activeExplain))) && (
        <div className="card explain-panel">
          <div className="card-header">
            <div className="card-title"><span className="card-title-icon">💡</span>Translation Learning Notes</div>
          </div>
          {explaining ? (
            <div className="typing-indicator" style={{ paddingLeft: 0 }}>
              <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
            </div>
          ) : (
            <div className="translation-notes">
              {translationDetails?.meaning && (
                <div className="note-block">
                  <div className="note-label">Meaning</div>
                  <p>{translationDetails.meaning}</p>
                </div>
              )}
              {translationDetails?.pronunciation && (
                <div className="note-block">
                  <div className="note-label">Pronunciation</div>
                  <p>{translationDetails.pronunciation}</p>
                </div>
              )}
              {translationDetails?.usage_tip && (
                <div className="note-block">
                  <div className="note-label">Usage Tip</div>
                  <p>{translationDetails.usage_tip}</p>
                </div>
              )}
              {translationDetails?.example_sentence && (
                <div className="note-block">
                  <div className="note-label">Example Sentence</div>
                  <p>{translationDetails.example_sentence}</p>
                </div>
              )}
              {translationDetails?.cultural_note && (
                <div className="note-block">
                  <div className="note-label">Cultural Note</div>
                  <p>{translationDetails.cultural_note}</p>
                </div>
              )}
              {!translationDetails && explanation && (
                <p style={{ fontSize: 14, lineHeight: 1.7, color: "var(--text-2)" }}>{explanation}</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
