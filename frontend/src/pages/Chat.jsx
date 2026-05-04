import { useMemo, useState } from "react";
import { chat, translate } from "../services/api";
import {
  PHRASE_CATEGORIES,
  QUIZ_QUESTIONS,
  SUPPORTED_LANGUAGES,
  VOCABULARY_WORDS,
} from "../data/languageQuestData";

const STARTER_STATS = { xp: 120, streak: 3, hearts: 5 };

function getLevel(xp) {
  return Math.max(1, Math.floor(xp / 120) + 1);
}

export default function Chat() {
  const [language, setLanguage] = useState("hi");
  const [mode, setMode] = useState("lesson");
  const [stats, setStats] = useState(STARTER_STATS);
  const [quizIndex, setQuizIndex] = useState(0);
  const [selected, setSelected] = useState("");
  const [feedback, setFeedback] = useState("");
  const [practiceText, setPracticeText] = useState("I want to learn something new today.");
  const [practiceResult, setPracticeResult] = useState("");
  const [coachNote, setCoachNote] = useState("");
  const [loading, setLoading] = useState(false);

  const languageName = SUPPORTED_LANGUAGES.find((item) => item.code === language)?.name || "Hindi";
  const quizList = useMemo(() => QUIZ_QUESTIONS.filter((item) => item.language === language), [language]);
  const quiz = quizList[quizIndex % Math.max(quizList.length, 1)] || QUIZ_QUESTIONS[0];
  const vocab = VOCABULARY_WORDS.find((item) => item.language === language)?.entries || [];
  const phraseGroups = PHRASE_CATEGORIES.filter((item) => ["greetings", "travel", "interview"].includes(item.key));

  function award(amount) {
    setStats((current) => ({ ...current, xp: current.xp + amount }));
  }

  function answerQuiz(choice) {
    if (selected) {
      return;
    }

    const isCorrect = choice === quiz.answer;
    setSelected(choice);
    setFeedback(isCorrect ? "Correct. You earned 20 XP." : `Not quite. Answer: ${quiz.answer}`);
    setStats((current) => ({
      ...current,
      xp: isCorrect ? current.xp + 20 : current.xp,
      hearts: isCorrect ? current.hearts : Math.max(0, current.hearts - 1),
    }));
  }

  function nextQuiz() {
    setQuizIndex((current) => current + 1);
    setSelected("");
    setFeedback("");
  }

  async function runPractice() {
    if (!practiceText.trim() || loading) {
      return;
    }

    setLoading(true);
    setPracticeResult("");
    setCoachNote("");

    try {
      const translated = await translate({
        text: practiceText,
        source: "en",
        target: language,
        tone: "simple beginner-friendly",
      });
      setPracticeResult(translated.translation || "");

      const coach = await chat(
        `Give one short learning tip for this ${languageName} translation practice: ${practiceText}`
      );
      setCoachNote(coach.reply || "Say it aloud twice, then use it in your own sentence.");
      award(15);
    } catch (error) {
      setCoachNote(error.message || "Practice is temporarily unavailable.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="quest-layout motion-safe:animate-[fade-in_0.35s_ease]">
      <div className="quest-hero">
        <div>
          <div className="hero-eyebrow">
            <span className="hero-eyebrow-dot" />
            Language Quest
          </div>
          <h1>Build a streak, learn useful phrases, and practice with AI.</h1>
          <p>Short lessons, quick quizzes, and translation drills for everyday language confidence.</p>
        </div>
        <div className="quest-score-card">
          <span>Level {getLevel(stats.xp)}</span>
          <strong>{stats.xp} XP</strong>
          <div className="quest-progress">
            <div style={{ width: `${Math.min(100, stats.xp % 120)}%` }} />
          </div>
        </div>
      </div>

      <div className="quest-stats">
        <div className="quest-stat"><span>Streak</span><strong>{stats.streak} days</strong></div>
        <div className="quest-stat"><span>Hearts</span><strong>{stats.hearts}/5</strong></div>
        <div className="quest-stat"><span>Target</span><strong>{languageName}</strong></div>
      </div>

      <div className="quest-toolbar">
        <select value={language} onChange={(event) => setLanguage(event.target.value)}>
          {SUPPORTED_LANGUAGES.map((item) => (
            <option key={item.code} value={item.code}>{item.name}</option>
          ))}
        </select>
        {["lesson", "quiz", "practice"].map((item) => (
          <button
            key={item}
            type="button"
            className={`btn ${mode === item ? "btn-primary" : "btn-ghost"}`}
            onClick={() => setMode(item)}
          >
            {item[0].toUpperCase() + item.slice(1)}
          </button>
        ))}
      </div>

      {mode === "lesson" ? (
        <div className="quest-grid">
          <section className="card">
            <div className="card-header">
              <div className="card-title">Core Vocabulary</div>
              <div className="badge-live"><span className="dot" />Daily</div>
            </div>
            <div className="lesson-list">
              {vocab.map((item) => (
                <article key={item.word} className="lesson-card">
                  <strong>{item.word}</strong>
                  <span>{item.meaning}</span>
                  <p>{item.example}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="card">
            <div className="card-header">
              <div className="card-title">Useful Phrase Packs</div>
              <div className="badge-live"><span className="dot" />Ready</div>
            </div>
            <div className="lesson-list">
              {phraseGroups.map((group) => (
                <article key={group.key} className="lesson-card">
                  <strong>{group.label}</strong>
                  {group.phrases.slice(0, 2).map((phrase) => (
                    <p key={phrase.text}>{phrase.text}: {phrase.translations[language] || phrase.text}</p>
                  ))}
                </article>
              ))}
            </div>
          </section>
        </div>
      ) : null}

      {mode === "quiz" ? (
        <section className="card quest-panel">
          <div className="card-title">{quiz.question}</div>
          <div className="quiz-options">
            {quiz.choices.map((choice) => (
              <button
                key={choice}
                type="button"
                className={`quiz-choice${selected === choice ? " selected" : ""}${selected && choice === quiz.answer ? " correct" : ""}`}
                onClick={() => answerQuiz(choice)}
              >
                {choice}
              </button>
            ))}
          </div>
          {feedback ? (
            <div className="quest-feedback">
              <p>{feedback}</p>
              <button type="button" className="btn btn-primary" onClick={nextQuiz}>Next challenge</button>
            </div>
          ) : null}
        </section>
      ) : null}

      {mode === "practice" ? (
        <section className="card quest-panel">
          <div className="card-header">
            <div className="card-title">AI Translation Practice</div>
            <div className="badge-live"><span className="dot" />Coach</div>
          </div>
          <label className="input-label">English sentence</label>
          <textarea
            className="textarea-main"
            value={practiceText}
            onChange={(event) => setPracticeText(event.target.value)}
          />
          <div className="action-row">
            <div className="spacer" />
            <button type="button" className="btn btn-primary" onClick={runPractice} disabled={loading}>
              {loading ? (
                <>
                  <div className="spinner" /> Checking...
                </>
              ) : (
                `Practice ${languageName}`
              )}
            </button>
          </div>
          {(practiceResult || coachNote || loading) ? (
            <div className="practice-result-card">
              <span>Coach Chat</span>
              <div className="chat-messages !min-h-0 !p-0">
                <div className="msg-wrapper user">
                  <div className="msg-avatar">You</div>
                  <div className="msg-bubble">{practiceText}</div>
                </div>
                {practiceResult ? (
                  <div className="msg-wrapper bot">
                    <div className="msg-avatar">AI</div>
                    <div className="msg-bubble">
                      <strong>{practiceResult}</strong>
                    </div>
                  </div>
                ) : null}
                {coachNote ? (
                  <div className="msg-wrapper bot">
                    <div className="msg-avatar">Tip</div>
                    <div className="msg-bubble">{coachNote}</div>
                  </div>
                ) : null}
                {loading ? (
                  <div className="typing-indicator">
                    <span />
                    <span />
                    <span />
                  </div>
                ) : null}
              </div>
            </div>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}
