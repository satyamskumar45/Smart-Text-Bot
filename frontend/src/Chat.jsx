import { useEffect, useMemo, useState } from "react";
import { translate, explainTranslation } from "../services/api";
import {
  SUPPORTED_LANGUAGES,
  DAILY_WORDS,
  QUIZ_QUESTIONS,
  VOCABULARY_WORDS,
  PHRASE_CATEGORIES,
} from "../data/languageQuestData";

const LEVEL_THRESHOLDS = [0, 100, 250, 500, 900, 1400];
const STORAGE_KEY = "languageQuestStats";

function buildStats(saved) {
  const today = new Date().toISOString().slice(0, 10);
  if (!saved) {
    return { xp: 240, streak: 5, lastActive: today };
  }

  const stats = { ...saved };
  if (stats.lastActive !== today) {
    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    stats.streak = stats.lastActive === yesterday ? stats.streak + 1 : 1;
    stats.lastActive = today;
  }
  return stats;
}

function clampLevel(xp) {
  return LEVEL_THRESHOLDS.filter((threshold) => xp >= threshold).length;
}

function getLevelProgress(xp) {
  const level = clampLevel(xp);
  const currentThreshold = LEVEL_THRESHOLDS[level - 1] ?? 0;
  const nextThreshold = LEVEL_THRESHOLDS[level] ?? currentThreshold + 100;
  return Math.min(100, Math.floor(((xp - currentThreshold) / (nextThreshold - currentThreshold)) * 100));
}

function getDailyWord() {
  const index = Math.floor(Date.now() / 86400000) % DAILY_WORDS.length;
  return DAILY_WORDS[index];
}

export default function Chat() {
  const [language, setLanguage] = useState("en");
  const [section, setSection] = useState("daily");
  const [stats, setStats] = useState(() => buildStats(null));
  const [quizIndex, setQuizIndex] = useState(0);
  const [quizAnswer, setQuizAnswer] = useState(null);
  const [quizFeedback, setQuizFeedback] = useState("");
  const [practiceText, setPracticeText] = useState("I would like a coffee.");
  const [practiceOutput, setPracticeOutput] = useState("");
  const [practiceNotes, setPracticeNotes] = useState(null);
  const [practiceLoading, setPracticeLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    const parsed = saved ? JSON.parse(saved) : null;
    const updated = buildStats(parsed);
    setStats(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  }, []);

  const saveStats = (nextStats) => {
    setStats(nextStats);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextStats));
  };

  const rewardXp = (amount) => {
    const next = { ...stats, xp: stats.xp + amount };
    saveStats(next);
  };

  const dailyWord = useMemo(() => getDailyWord(), []);
  const currentQuizList = useMemo(
    () => QUIZ_QUESTIONS.filter((item) => item.language === language),
    [language]
  );
  const currentQuiz = currentQuizList[quizIndex % currentQuizList.length] || currentQuizList[0] || {
    question: "Select a supported language to start the quiz.",
    choices: [],
    answer: "",
    explanation: "",
  };

  const vocabulary = useMemo(
    () => VOCABULARY_WORDS.find((item) => item.language === language)?.entries || [],
    [language]
  );

  const handleSection = (value) => {
    setSection(value);
    setQuizAnswer(null);
    setQuizFeedback("");
    setError("");
  };

  const selectQuizAnswer = (choice) => {
    if (!currentQuiz || quizAnswer) return;
    const correct = choice === currentQuiz.answer;
    setQuizAnswer(choice);
    setQuizFeedback(correct ? "Correct! Great job." : "Almost there — try the next one.");
    if (correct) {
      rewardXp(25);
    }
  };

  const nextQuiz = () => {
    setQuizIndex((prev) => prev + 1);
    setQuizAnswer(null);
    setQuizFeedback("");
  };

  const runPractice = async () => {
    if (!practiceText.trim()) return;
    setPracticeLoading(true);
    setPracticeOutput("");
    setPracticeNotes(null);
    setError("");

    try {
      const result = await translate({ text: practiceText, source: "en", target: language });
      const translation = result?.data?.translated_text || result?.data?.translation || "";
      setPracticeOutput(translation);
      const detailRes = await explainTranslation({ text: practiceText, translated_text: translation, source_lang: "en", target_lang: language });
      const detail = detailRes?.data || null;
      setPracticeNotes(detail || null);
      rewardXp(15);
    } catch (err) {
      console.error("[LANGUAGE QUEST ERROR]", err);
      setError(err.message || "Translation practice failed.");
    } finally {
      setPracticeLoading(false);
    }
  };

  const actionButtons = [
    { key: "daily", label: "Daily Word" },
    { key: "quiz", label: "Daily Quiz" },
    { key: "vocab", label: "Vocabulary" },
    { key: "phrases", label: "Learn Phrases" },
    { key: "travel", label: "Travel Basics" },
    { key: "interview", label: "Interview Phrases" },
    { key: "practice", label: "Practice Translation" },
  ];

  return (
    <div className="quest-layout">
      <div className="page-header">
        <h1>Language Quest</h1>
        <p>Turn your language goals into a streak-driven learning journey with daily challenges, quizzes, and translation practice.</p>
      </div>

      <div className="quest-top-row">
        <div className="quest-card streak-card">
          <div className="card-title">🔥 Streak</div>
          <div className="card-value">{stats.streak} Day{stats.streak === 1 ? "" : "s"}</div>
          <div className="card-note">Keep the streak alive by practicing every day.</div>
        </div>
        <div className="quest-card xp-card">
          <div className="card-title">⭐ XP</div>
          <div className="card-value">{stats.xp}</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${getLevelProgress(stats.xp)}%` }} />
          </div>
          <div className="card-note">Level {clampLevel(stats.xp)} progress</div>
        </div>
        <div className="quest-card level-card">
          <div className="card-title">🏆 Level</div>
          <div className="card-value">{clampLevel(stats.xp)}</div>
          <div className="card-note">Unlock new phrase sets and quick wins.</div>
        </div>
      </div>

      <div className="quest-select-row">
        <div className="lang-pill-row">
          {SUPPORTED_LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              className={`lang-pill${language === lang.code ? " active" : ""}`}
              onClick={() => setLanguage(lang.code)}
            >
              <span>{lang.emoji}</span> {lang.name}
            </button>
          ))}
        </div>
      </div>

      <div className="action-menu">
        {actionButtons.map((item) => (
          <button
            key={item.key}
            className={`btn btn-ghost action-button${section === item.key ? " active" : ""}`}
            onClick={() => handleSection(item.key)}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="quest-content-grid">
        <div className="card daily-challenge-card">
          <div className="card-header">
            <div className="card-title">🎯 Daily Word Challenge</div>
            <div className="badge-live"><span className="dot" />New Today</div>
          </div>
          <div className="challenge-word">{dailyWord.word}</div>
          <div className="challenge-meta">{SUPPORTED_LANGUAGES.find((lang) => lang.code === dailyWord.language)?.name}</div>
          <div className="challenge-block">
            <div className="challenge-label">Meaning</div>
            <p>{dailyWord.meaning}</p>
          </div>
          <div className="challenge-block">
            <div className="challenge-label">Pronunciation</div>
            <p>{dailyWord.pronunciation}</p>
          </div>
          <div className="challenge-block">
            <div className="challenge-label">Example</div>
            <p>{dailyWord.example}</p>
          </div>
          <div className="challenge-tip">{dailyWord.tip}</div>
        </div>

        <div className="card section-card">
          <div className="card-header">
            <div className="card-title">{actionButtons.find((item) => item.key === section)?.label}</div>
            <div className="badge-live"><span className="dot" />Focus Mode</div>
          </div>

          {error && (
            <div className="alert-card">⚠ {error}</div>
          )}

          {section === "quiz" && (
            <div className="quiz-card">
              <div className="quiz-question">{currentQuiz.question}</div>
              <div className="quiz-options">
                {currentQuiz.choices.map((choice) => (
                  <button
                    key={choice}
                    className={`btn btn-secondary quiz-option${quizAnswer === choice ? " selected" : ""}${quizAnswer && choice === currentQuiz.answer ? " correct" : ""}`}
                    onClick={() => selectQuizAnswer(choice)}
                    disabled={!!quizAnswer}
                  >
                    {choice}
                  </button>
                ))}
              </div>
              {quizFeedback && (
                <div className="quiz-feedback">
                  <p>{quizFeedback}</p>
                  {quizAnswer && (
                    <button className="btn btn-primary" onClick={nextQuiz}>Next Question</button>
                  )}
                </div>
              )}
              {quizAnswer && !quizFeedback.includes("Correct") && (
                <div className="hint-block">Answer: {currentQuiz.answer}</div>
              )}
            </div>
          )}

          {section === "vocab" && (
            <div className="grid-list">
              {vocabulary.map((item) => (
                <div key={item.word} className="phrase-card">
                  <div className="phrase-title">{item.word}</div>
                  <div className="phrase-sub">{item.meaning}</div>
                  <div className="phrase-small">{item.pronunciation}</div>
                  <p>{item.example}</p>
                </div>
              ))}
            </div>
          )}

          {section === "phrases" && (
            <div className="grid-list">
              {PHRASE_CATEGORIES.map((category) => (
                <div key={category.key} className="phrase-group">
                  <div className="phrase-heading">{category.label}</div>
                  {category.phrases.map((phrase) => (
                    <div key={phrase.text} className="phrase-card">
                      <div className="phrase-title">{phrase.text}</div>
                      <div className="phrase-sub">{phrase.translations[language]}</div>
                      <div className="phrase-small">{phrase.pronunciation[language]}</div>
                      <p>{phrase.tip}</p>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}

          {section === "travel" && (
            <div className="grid-list">
              {PHRASE_CATEGORIES.find((category) => category.key === "travel")?.phrases.map((phrase) => (
                <div key={phrase.text} className="phrase-card">
                  <div className="phrase-title">{phrase.text}</div>
                  <div className="phrase-sub">{phrase.translations[language]}</div>
                  <div className="phrase-small">{phrase.pronunciation[language]}</div>
                  <p>{phrase.tip}</p>
                </div>
              ))}
            </div>
          )}

          {section === "interview" && (
            <div className="grid-list">
              {PHRASE_CATEGORIES.find((category) => category.key === "interview")?.phrases.map((phrase) => (
                <div key={phrase.text} className="phrase-card">
                  <div className="phrase-title">{phrase.text}</div>
                  <div className="phrase-sub">{phrase.translations[language]}</div>
                  <div className="phrase-small">{phrase.pronunciation[language]}</div>
                  <p>{phrase.tip}</p>
                </div>
              ))}
            </div>
          )}

          {section === "practice" && (
            <div className="practice-panel">
              <label className="input-label">Translate to {SUPPORTED_LANGUAGES.find((lang) => lang.code === language)?.name}</label>
              <textarea
                className="textarea-main"
                value={practiceText}
                onChange={(e) => setPracticeText(e.target.value)}
                rows={4}
              />
              <div className="action-row" style={{ marginTop: 16 }}>
                <button className="btn btn-primary" onClick={runPractice} disabled={practiceLoading || !practiceText.trim()}>
                  {practiceLoading ? <><div className="spinner" /> Translating…</> : "Practice Translation"}
                </button>
              </div>
              {practiceOutput && (
                <div className="practice-result-card">
                  <div className="phrase-title">Translation</div>
                  <p>{practiceOutput}</p>
                  {practiceNotes && (
                    <div className="translation-tips">
                      {practiceNotes.meaning && (
                        <div className="note-block"><div className="note-label">Meaning</div><p>{practiceNotes.meaning}</p></div>
                      )}
                      {practiceNotes.pronunciation && (
                        <div className="note-block"><div className="note-label">Pronunciation</div><p>{practiceNotes.pronunciation}</p></div>
                      )}
                      {practiceNotes.usage_tip && (
                        <div className="note-block"><div className="note-label">Usage Tip</div><p>{practiceNotes.usage_tip}</p></div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
