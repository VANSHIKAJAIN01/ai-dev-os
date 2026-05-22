"use client";
// ChatWindow.tsx — The main chat interface
//
// How streaming works here:
// 1. User sends a message
// 2. We call the backend /api/chat endpoint
// 3. The backend streams tokens back one by one
// 4. We read each chunk from the stream and append it to the message
// 5. The UI updates in real-time as tokens arrive (like ChatGPT typing)
//
// This uses the browser's fetch + ReadableStream API — no WebSockets needed.

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I'm your AI Dev OS assistant. Ingest a GitHub repo and then ask me anything about the codebase.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [repoUrl, setRepoUrl] = useState("");
  const [ingesting, setIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function ingestRepo() {
    if (!repoUrl.trim()) return;
    setIngesting(true);
    setIngestStatus("Fetching and indexing repo...");

    try {
      const res = await fetch(`${BACKEND_URL}/api/ingest/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl, project_id: "project-1" }),
      });
      const data = await res.json();
      setIngestStatus(`Done! Indexed ${data.chunks_ingested} chunks.`);
    } catch {
      setIngestStatus("Error ingesting repo. Is the backend running?");
    } finally {
      setIngesting(false);
    }
  }

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setLoading(true);

    // Add user message immediately
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);

    // Add empty assistant message that we'll fill in as tokens stream in
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const res = await fetch(`${BACKEND_URL}/api/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage, project_id: "project-1" }),
      });

      if (!res.body) throw new Error("No response body");

      // Read the stream token by token
      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);

        // Append each chunk to the last (assistant) message
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: updated[updated.length - 1].content + chunk,
          };
          return updated;
        });
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "Error connecting to backend. Make sure it's running on port 8000.",
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Ingest bar */}
      <div className="border-b border-gray-800 p-3 bg-gray-900">
        <div className="flex gap-2 items-center">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="GitHub repo URL (e.g. https://github.com/user/repo)"
            className="flex-1 bg-gray-800 text-sm text-gray-100 rounded-lg px-3 py-2 outline-none border border-gray-700 focus:border-blue-500 placeholder-gray-500"
          />
          <button
            onClick={ingestRepo}
            disabled={ingesting}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm rounded-lg font-medium transition-colors"
          >
            {ingesting ? "Indexing..." : "Ingest Repo"}
          </button>
        </div>
        {ingestStatus && (
          <p className="text-xs text-gray-400 mt-1.5 px-1">{ingestStatus}</p>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-blue-600 text-white rounded-br-sm"
                  : "bg-gray-800 text-gray-100 rounded-bl-sm"
              }`}
            >
              {msg.content}
              {/* Show blinking cursor while streaming */}
              {loading && i === messages.length - 1 && msg.role === "assistant" && (
                <span className="inline-block w-1.5 h-4 bg-gray-400 ml-0.5 animate-pulse" />
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="border-t border-gray-800 p-4 bg-gray-900">
        <div className="flex gap-3 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Ask anything about your codebase... (Enter to send, Shift+Enter for newline)"
            rows={1}
            className="flex-1 bg-gray-800 text-gray-100 rounded-xl px-4 py-3 text-sm outline-none border border-gray-700 focus:border-blue-500 resize-none placeholder-gray-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-5 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white text-sm rounded-xl font-medium transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
