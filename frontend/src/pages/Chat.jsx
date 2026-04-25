import { useEffect, useMemo, useState } from "react";
import {
  explainTranslation,
  fetchFavorites,
  fetchHistory,
  fetchLearningProgress,
  saveLearningProgress,
  toggleFavorite,
  translate,
} from "../services/api";
import {
  SUPPORTED_LANGUAGES,
  DAILY_WORDS,
  QUIZ_QUESTIONS,
  VOCABULARY_WORDS,
  PHRASE_CATEGORIES,
} from "../data/languageQuestData";

const LEVEL_THRESHOLDS = [0, 100, 250, 500, 900, 1400];
const ACTIONS = [
  { key: "daily", label: "Daily Challenge" },
  { key: "quiz", label: "Quiz Mode" },
  { key: "vocab", label: "Vocabulary Cards" },
  { key: "phrases", label: "Phrase Bank" },
  { key: "practice", label: "Translate Practice" },
];

function levelProgress(xp) {
  const level = LEVEL_THRESHOLDS.filter((threshold) => xp >= threshold).length || 1;
  const current = LEVEL_THRESHOLDS[level - 1] ?? 0;
  const next = LEVEL_THRESHOLDS[level] ?? current + 100;
  return {
    level,
    percent: Math.min(100, Math.floor(((xp - current) / (next - current || 1)) * 100)),
  };
}

function getDailyWord() {
  const index = Math.floor(Date.now() / 86400000) % DAILY_WORDS.length;
  return DAILY_WORDS[index];
}

function buildLearningState(snapshot, historyItems, favoriteItems) {
  const learningHistory = (historyItems || []).filter((item) => item.module_type === "learning_assistant");
  const phraseFavorites = {};
  (favoriteItems || [])
    .filter((item) => item.module_type === "learning_assistant" && item.metadata?.activity_type === "phrase")
    .forEach((item) => {
      if (item.metadata?.phrase_key) {
        phraseFavorites[item.metadata.phrase_key] = item.id;
      }
    });

  return {
    xp: snapshot?.xp || 0,
    level: snapshot?.level || 1,
    currentStreak: snapshot?.current_streak || 0,
    bestStreak: snapshot?.best_streak || 0,
    completedQuizzes: Array.from(new Set(
      learningHistory
        .filter((item) => item.metadata?.activity_type === "quiz" && item.metadata?.question)
        .map((item) => `${item.metadata.language}:${item.metadata.question}`)
    )),
    learnedVocabulary: Array.from(new Set(
      learningHistory
        .filter((item) => item.metadata?.activity_type === "vocabulary" && item.metadata?.word)
        .map((item) => `${item.metadata.language}:${item.metadata.word}`)
    )),
    favoritePhraseIds: phraseFavorites,
    recentTranslations: learningHistory
      .filter((item) => item.metadata?.activity_type === "practice")
      .slice(0, 8)
      .map((item) => ({
        id: item.id,
        source: item.input_text,
        output: item.output_text,
        targetLang: item.metadata?.language || "en",
        createdAt: item.created_at,
      })),
  };
}

export default function Chat() {
  const [language, setLanguage] = useState("es");
  const [section, setSection] = useState("daily");
  const [progress, setProgress] = useState({
    xp: 0,
    level: 1,
    currentStreak: 0,
    bestStreak: 0,
    completedQuizzes: [],
    learnedVocabulary: [],
    favoritePhraseIds: {},
    recentTranslations: [],
  });
  const [quizAnswer, setQuizAnswer] = useState(null);
  const [quizFeedback, setQuizFeedback] = useState("");
  const [practiceText, setPracticeText] = useState("I would like a coffee.");
  const [practiceOutput, setPracticeOutput] = useState("");
  const [practiceNotes, setPracticeNotes] = useState(null);
  const [practiceLoading, setPracticeLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");

  const showToast = (message) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 1800);
  };

  const refreshProgress = async () => {
    setLoading(true);
    setError("");
    try {
      const [snapshot, historyResponse, favoritesResponse] = await Promise.all([
        fetchLearningProgress(),
        fetchHistory(),
        fetchFavorites(),
      ]);
      setProgress(buildLearningState(snapshot, historyResponse.items || [], favoritesResponse.items || []));
    } catch (err) {
      console.error("[LEARNING LOAD ERROR]", err);
      setError(err.message || "Unable to load learning progress.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshProgress();
  }, []);

  const currentQuizList = useMemo(
    () => QUIZ_QUESTIONS.filter((item) => item.language === language),
    [language]
  );
  const completedQuizSet = useMemo(() => new Set(progress.completedQuizzes), [progress.completedQuizzes]);
  const availableQuizzes = useMemo(
    () => currentQuizList.filter((item) => !completedQuizSet.has(`${language}:${item.question}`)),
    [currentQuizList, completedQuizSet, language]
  );
  const currentQuiz = useMemo(
    () => availableQuizzes[0] || currentQuizList[0],
    [availableQuizzes, currentQuizList]
  );
  const vocabulary = useMemo(
    () => VOCABULARY_WORDS.find((item) => item.language === language)?.entries || [],
    [language]
  );
  const dailyWord = useMemo(() => getDailyWord(), []);
  const progressBar = levelProgress(progress.xp);

  const updateFromBackendProgress = (backendProgress) => {
    if (!backendProgress) return;
    setProgress((current) => ({
      ...current,
      xp: backendProgress.xp ?? current.xp,
      level: backendProgress.level ?? current.level,
      currentStreak: backendProgress.current_streak ?? current.currentStreak,
      bestStreak: backendProgress.best_streak ?? current.bestStreak,
    }));
  };

  const markVocabularyLearned = async (entry) => {
    const key = `${language}:${entry.word}`;
    if (progress.learnedVocabulary.includes(key)) return;
    try {
      const response = await saveLearningProgress({
        activity_type: "vocabulary",
        language,
        input_text: entry.word,
        output_text: entry.meaning,
        xp_delta: 10,
        metadata: {
          word: entry.word,
          pronunciation: entry.pronunciation,
          example: entry.example,
        },
      });
      updateFromBackendProgress(response.progress);
      setProgress((current) => ({
        ...current,
        learnedVocabulary: [...current.learnedVocabulary, key],
      }));
      showToast("+10 XP vocabulary saved");
    } catch (err) {
      setError(err.message || "Could not save vocabulary progress.");
    }
  };

  const togglePhraseFavorite = async (phrase, phraseKey) => {
    const existingId = progress.favoritePhraseIds[phraseKey];
    try {
      if (existingId) {
        await toggleFavorite(existingId, false);
        setProgress((current) => {
          const next = { ...current.favoritePhraseIds };
          delete next[phraseKey];
          return { ...current, favoritePhraseIds: next };
        });
        showToast("Phrase removed from favorites");
        return;
      }

      const response = await saveLearningProgress({
        activity_type: "phrase",
        language,
        input_text: phrase.text,
        output_text: phrase.translations[language],
        xp_delta: 5,
        favorite: true,
        metadata: {
          phrase_key: phraseKey,
          pronunciation: phrase.pronunciation[language],
          tip: phrase.tip,
        },
      });
      updateFromBackendProgress(response.progress);
      setProgress((current) => ({
        ...current,
        favoritePhraseIds: {
          ...current.favoritePhraseIds,
          [phraseKey]: response.history_id,
        },
      }));
      showToast("Phrase saved to favorites");
    } catch (err) {
      setError(err.message || "Could not update phrase favorite.");
    }
  };

  const selectQuizAnswer = async (choice) => {
    if (!currentQuiz || quizAnswer) return;
    setQuizAnswer(choice);
    if (choice !== currentQuiz.answer) {
      setQuizFeedback(`Not quite. Correct answer: ${currentQuiz.answer}`);
      return;
    }

    try {
      const response = await saveLearningProgress({
        activity_type: "quiz",
        language,
        input_text: currentQuiz.question,
        output_text: currentQuiz.answer,
        xp_delta: 25,
        metadata: {
          question: currentQuiz.question,
          explanation: currentQuiz.explanation,
        },
      });
      updateFromBackendProgress(response.progress);
      setProgress((current) => ({
        ...current,
        completedQuizzes: [...current.completedQuizzes, `${language}:${currentQuiz.question}`],
      }));
      setQuizFeedback("Correct. Quiz progress saved.");
      showToast("+25 XP quiz complete");
    } catch (err) {
      setError(err.message || "Could not save quiz progress.");
      setQuizFeedback("");
    }
  };

  const runPractice = async () => {
    if (!practiceText.trim() || practiceLoading) return;
    setPracticeLoading(true);
    setPracticeOutput("");
    setPracticeNotes(null);
    setError("");
    try {
      const translation = await translate(practiceText, "en", language);
      setPracticeOutput(translation.translated_text);
      const details = await explainTranslation(practiceText, translation.translated_text, "en", language);
      setPracticeNotes(details);

      const response = await saveLearningProgress({
        activity_type: "practice",
        language,
        input_text: practiceText,
        output_text: translation.translated_text,
        xp_delta: 15,
        metadata: {
          notes: details,
        },
      });
      updateFromBackendProgress(response.progress);
      setProgress((current) => ({
        ...current,
        recentTranslations: [
          {
            id: response.history_id,
            source: practiceText,
            output: translation.translated_text,
            targetLang: language,
            createdAt: new Date().toISOString(),
          },
          ...current.recentTranslations,
        ].slice(0, 8),
      }));
      showToast("+15 XP practice saved");
    } catch (err) {
      console.error("[LEARNING PRACTICE ERROR]", err);
      setError(err.message || "Translation practice failed.");
    } finally {
      setPracticeLoading(false);
    }
  };

  const currentLanguageName = SUPPORTED_LANGUAGES.find((item) => item.code === language)?.name || "Language";

  return (
    <div className="quest-layout">
      <div className="page-header">
        <h1>Smart Learning Assistant</h1>
        <p>Build vocabulary, complete quizzes, track streaks, earn XP, and save practice history across 6 languages.</p>
      </div>

      {loading && <div className="loading-card">Loading learning progress...</div>}
      {error && <div className="status-error">{error}</div>}

      <div className="quest-top-row">
        <div className="quest-card streak-card">
          <div className="card-title">Streak</div>
          <div className="card-value">{progress.currentStreak} day{progress.currentStreak === 1 ? "" : "s"}</div>
          <div className="card-note">Best streak: {progress.bestStreak}</div>
        </div>

        <div className="quest-card xp-card">
          <div className="card-title">XP</div>
          <div className="card-value">{progress.xp}</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progressBar.percent}%` }} />
          </div>
          <div className="card-note">Level {progressBar.level}</div>
        </div>

        <div className="quest-card level-card">
          <div className="card-title">Progress</div>
          <div className="card-value">{progress.learnedVocabulary.length}</div>
          <div className="card-note">Vocabulary cards learned</div>
          <div className="card-note">Saved practice sessions: {progress.recentTranslations.length}</div>
        </div>
      </div>

      <div className="quest-select-row">
        <div className="lang-pill-row">
          {SUPPORTED_LANGUAGES.map((item) => (
            <button
              key={item.code}
              className={`lang-pill${language === item.code ? " active" : ""}`}
              onClick={() => {
                setLanguage(item.code);
                setQuizAnswer(null);
                setQuizFeedback("");
                setError("");
              }}
            >
              {item.name}
            </button>
          ))}
        </div>
      </div>

      <div className="action-menu">
        {ACTIONS.map((item) => (
          <button
            key={item.key}
            className={`btn btn-ghost action-button${section === item.key ? " active" : ""}`}
            onClick={() => {
              setSection(item.key);
              setQuizAnswer(null);
              setQuizFeedback("");
            }}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="quest-content-grid">
        <div className="card daily-challenge-card">
          <div className="card-header">
            <div className="card-title">Daily Word</div>
            <div className="badge-live">
              <span className="dot" />
              New Today
            </div>
          </div>
          <div className="challenge-word">{dailyWord.word}</div>
          <div className="challenge-meta">
            {SUPPORTED_LANGUAGES.find((item) => item.code === dailyWord.language)?.name}
          </div>
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
            <div className="card-title">{ACTIONS.find((item) => item.key === section)?.label}</div>
            <button className="btn btn-ghost" onClick={refreshProgress}>Refresh Progress</button>
          </div>

          {section === "daily" && (
            <div className="note-block">
              <div className="note-label">Today's goal</div>
              <p>Learn one vocabulary card, complete one quiz question, and save one practice translation to keep your streak alive.</p>
            </div>
          )}

          {section === "quiz" && currentQuiz && (
            <div className="quiz-card">
              {availableQuizzes.length === 0 ? (
                <div className="note-block">
                  <div className="note-label">Quiz complete</div>
                  <p>You have finished the current quiz set for {currentLanguageName}. Switch languages or come back later for more practice.</p>
                </div>
              ) : (
                <>
                  <div className="quiz-question">{currentQuiz.question}</div>
                  <div className="quiz-options">
                    {currentQuiz.choices.map((choice) => (
                      <button
                        key={choice}
                        className={`btn btn-secondary quiz-option${quizAnswer === choice ? " selected" : ""}`}
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
                      {currentQuiz.explanation && <p>{currentQuiz.explanation}</p>}
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {section === "vocab" && (
            <div className="grid-list">
              {vocabulary.map((entry) => {
                const learned = progress.learnedVocabulary.includes(`${language}:${entry.word}`);
                return (
                  <div key={entry.word} className="phrase-card">
                    <div className="phrase-card-header">
                      <div>
                        <div className="phrase-title">{entry.word}</div>
                        <div className="phrase-sub">{entry.meaning}</div>
                      </div>
                      <button className="btn btn-ghost phrase-fav" onClick={() => markVocabularyLearned(entry)} disabled={learned}>
                        {learned ? "Learned" : "Mark Learned"}
                      </button>
                    </div>
                    <div className="phrase-small">{entry.pronunciation}</div>
                    <p>{entry.example}</p>
                  </div>
                );
              })}
            </div>
          )}

          {section === "phrases" && (
            <div className="grid-list">
              {PHRASE_CATEGORIES.map((category) => (
                <div key={category.key} className="phrase-group">
                  <div className="phrase-heading">{category.label}</div>
                  {category.phrases.map((phrase) => {
                    const phraseKey = `${category.key}:${phrase.text}:${language}`;
                    const favorite = Boolean(progress.favoritePhraseIds[phraseKey]);
                    return (
                      <div key={phraseKey} className="phrase-card">
                        <div className="phrase-card-header">
                          <div>
                            <div className="phrase-title">{phrase.text}</div>
                            <div className="phrase-sub">{phrase.translations[language]}</div>
                          </div>
                          <button
                            className={`btn btn-ghost phrase-fav${favorite ? " active" : ""}`}
                            onClick={() => togglePhraseFavorite(phrase, phraseKey)}
                          >
                            {favorite ? "Favorited" : "Favorite"}
                          </button>
                        </div>
                        <div className="phrase-small">{phrase.pronunciation[language]}</div>
                        <p>{phrase.tip}</p>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          )}

          {section === "practice" && (
            <div className="practice-panel">
              <label className="input-label">Translate to {currentLanguageName}</label>
              <textarea
                className="textarea-main"
                value={practiceText}
                onChange={(event) => setPracticeText(event.target.value)}
                rows={4}
              />
              <div className="action-row" style={{ marginTop: 16 }}>
                <button className="btn btn-primary" onClick={runPractice} disabled={practiceLoading || !practiceText.trim()}>
                  {practiceLoading ? "Practicing..." : "Save Practice Session"}
                </button>
              </div>

              {practiceOutput && (
                <div className="practice-result-card">
                  <div className="phrase-title">Translation</div>
                  <p>{practiceOutput}</p>
                  {practiceNotes?.meaning && (
                    <div className="translation-tips">
                      <div className="note-block">
                        <div className="note-label">Meaning</div>
                        <p>{practiceNotes.meaning}</p>
                      </div>
                      {practiceNotes.pronunciation && (
                        <div className="note-block">
                          <div className="note-label">Pronunciation</div>
                          <p>{practiceNotes.pronunciation}</p>
                        </div>
                      )}
                      {practiceNotes.usage_tip && (
                        <div className="note-block">
                          <div className="note-label">Usage Tip</div>
                          <p>{practiceNotes.usage_tip}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {progress.recentTranslations.length > 0 && (
                <div className="recent-list">
                  <div className="phrase-heading">Saved Practice History</div>
                  {progress.recentTranslations.map((item) => (
                    <div key={item.id} className="translation-item">
                      <div className="translation-meta">
                        <span>{item.targetLang.toUpperCase()} · {new Date(item.createdAt).toLocaleDateString()}</span>
                        <button className="btn btn-ghost" onClick={() => navigator.clipboard.writeText(item.output)}>
                          Copy
                        </button>
                      </div>
                      <div>
                        <div className="phrase-sub">Source: {item.source}</div>
                        <div className="phrase-small">Output: {item.output}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
