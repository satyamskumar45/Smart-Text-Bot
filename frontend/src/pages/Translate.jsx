import { useState } from "react";
import LANGUAGES from "../data/languages";
import { translate } from "../services/api";

const COMMON_LANGUAGES = ["en", "hi", "es", "fr", "de", "ja", "ar", "zh", "pt", "ru"];

function languageOptions() {
  const priority = LANGUAGES.filter((item) => COMMON_LANGUAGES.includes(item.code));
  const rest = LANGUAGES.filter((item) => !COMMON_LANGUAGES.includes(item.code));
  return [...priority, ...rest];
}

export default function Translate() {
  const [fromLang, setFromLang] = useState("auto");
  const [toLang, setToLang] = useState("hi");
  const [tone, setTone] = useState("natural");
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [variants, setVariants] = useState({});
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState("");

  const options = languageOptions();

  function swap() {
    if (fromLang === "auto") {
      return;
    }
    setFromLang(toLang);
    setToLang(fromLang);
    setInput(output);
    setOutput(input);
    setVariants({});
  }

  async function run() {
    if (!input.trim() || loading) {
      return;
    }

    setLoading(true);
    setOutput("");
    setVariants({});

    try {
      const result = await translate({
        text: input,
        source: fromLang,
        target: toLang,
        tone,
        include_variants: true,
      });
      setOutput(result.translation || "");
      setVariants(result.variants || {});
    } catch (error) {
      setOutput(error.message || "Translation failed.");
    } finally {
      setLoading(false);
    }
  }

  async function copy(value, key) {
    if (!value) {
      return;
    }
    await navigator.clipboard.writeText(value);
    setCopied(key);
    window.setTimeout(() => setCopied(""), 1200);
  }

  return (
    <div className="translate-layout">
      <section className="translate-hero">
        <div>
          <div className="hero-eyebrow">
            <span className="hero-eyebrow-dot" />
            Translation Studio
          </div>
          <h1>Translate with tone, context, and polished alternatives.</h1>
          <p>Pick languages, choose a writing style, and compare formal, informal, and simple versions in one clean workspace.</p>
        </div>
        <div className="translate-hero-stat">
          <span>Characters</span>
          <strong>{input.length}</strong>
          <small>{input.trim() ? "Ready to translate" : "Waiting for text"}</small>
        </div>
      </section>

      <div className="translate-card">
        <div className="translate-controls">
          <label>
            <span>From</span>
            <select value={fromLang} onChange={(event) => setFromLang(event.target.value)}>
              <option value="auto">Auto detect</option>
              {options.map((language) => (
                <option key={language.code} value={language.code}>{language.name}</option>
              ))}
            </select>
          </label>
          <button type="button" className="swap-btn translate-swap" onClick={swap} title="Swap languages">Swap</button>
          <label>
            <span>To</span>
            <select value={toLang} onChange={(event) => setToLang(event.target.value)}>
              {options.map((language) => (
                <option key={language.code} value={language.code}>{language.name}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Tone</span>
            <select value={tone} onChange={(event) => setTone(event.target.value)}>
              <option value="natural">Natural</option>
              <option value="formal">Formal</option>
              <option value="informal conversational">Informal</option>
              <option value="simple beginner-friendly">Simple</option>
            </select>
          </label>
        </div>

        <div className="translate-editor">
          <div className="dual-pane">
            <div className="dual-pane-label">
              <span>Source</span>
              <small>{fromLang === "auto" ? "Auto detect" : fromLang.toUpperCase()}</small>
            </div>
            <textarea
              className="textarea-main"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Enter text to translate..."
            />
          </div>
          <div className="dual-pane">
            <div className="dual-pane-label">
              <span>Translation</span>
              <small>{toLang.toUpperCase()} · {tone}</small>
            </div>
            <textarea
              className="textarea-output"
              value={output}
              readOnly
              placeholder={loading ? "Translating..." : "Translation will appear here..."}
            />
          </div>
        </div>

        <div className="translate-actions">
          <button type="button" className="btn btn-ghost" onClick={() => copy(output, "main")}>
            {copied === "main" ? "Copied" : "Copy"}
          </button>
          <div className="translate-meta">
            <span>{input.trim().split(/\s+/).filter(Boolean).length} words</span>
            <span>{tone.replace(" conversational", "")}</span>
          </div>
          <button type="button" className="btn btn-primary" onClick={run} disabled={loading || !input.trim()}>
            {loading ? "Translating..." : "Translate"}
          </button>
        </div>
      </div>

      <div className="variant-grid">
        {["formal", "informal", "simple"].map((key) => (
          <article key={key} className={`variant-card translate-variant translate-variant-${key}`}>
            <div>
              <span>{key}</span>
              <button type="button" onClick={() => copy(variants[key], key)}>
                {copied === key ? "Copied" : "Copy"}
              </button>
            </div>
            <p>{variants[key] || "Run a translation to generate this version."}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
