import { useEffect, useRef, useState } from "react";
import { chat } from "../services/api";

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const autoResize = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  };

  const send = async () => {
    const text = input.trim();
    if (!text || loading) {
      return;
    }

    const userMessage = { role: "user", text, time: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
    setLoading(true);

    try {
      const response = await chat(text);
      const botMessage = {
        role: "bot",
        text: response.reply || response.response || "No response received.",
        time: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "⚠ Failed to reach the server. Is the backend running?",
          time: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      send();
    }
  };

  return (
    <div className="chat-layout">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">💬</div>
            <h3>Start a conversation</h3>
            <p>Type a message below to chat with the AI assistant.</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`msg-wrapper ${message.role}`}>
              <div className="msg-avatar">{message.role === "user" ? "U" : "🤖"}</div>
              <div>
                <div className="msg-bubble">{message.text}</div>
                <div className="msg-time">{formatTime(message.time)}</div>
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="msg-wrapper bot">
            <div className="msg-avatar">🤖</div>
            <div className="msg-bubble">
              <div className="typing-indicator">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-box">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(event) => {
              setInput(event.target.value);
              autoResize();
            }}
            onKeyDown={handleKey}
            placeholder="Ask anything... (Enter to send, Shift+Enter for new line)"
            rows={1}
          />
          <button
            className="chat-send-btn"
            onClick={send}
            disabled={!input.trim() || loading}
            title="Send message"
          >
            {loading ? <div className="spinner" style={{ borderTopColor: "#080c12" }} /> : "↑"}
          </button>
        </div>
      </div>
    </div>
  );
}
