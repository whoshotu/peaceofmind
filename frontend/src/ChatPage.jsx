import React, { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = "/api";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [pending, setPending] = useState([]);

  useEffect(() => {
    async function fetchPending() {
      try {
        const res = await axios.get(`${API_BASE}/admin/pending`);
        setPending(res.data.pending || []);
      } catch (_) {}
    }
    fetchPending();
  }, []);

  const sendMessage = async () => {
    if (!message) return;
    setChatLog((c) => [...c, { from: "user", text: message }]);
    setMessage("");
    const resp = await axios.post(`${API_BASE}/chat`, { messages: [{ role: "user", content: message }] });
    const reply = resp.data;
    setChatLog((c) => [...c, { from: "agent", text: reply.content || JSON.stringify(reply) }]);
  };

  const approveTask = async (taskId) => {
    await axios.post(`${API_BASE}/admin/approve`, { task_id: taskId });
    setPending((p) => p.filter((t) => t.id !== taskId));
  };

  return (
    <div>
      <div style={{ border: "1px solid #ddd", padding: "0.5rem", minHeight: 300, marginBottom: "1rem" }}>
        {chatLog.map((m, i) => (
          <div key={i} style={{ marginBottom: "0.5rem" }}>
            <strong>{m.from}:</strong> {m.text}
          </div>
        ))}
      </div>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <input
          type="text"
          placeholder="Ask a question..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={{ flex: 1, padding: "0.4rem" }}
        />
        <button onClick={sendMessage} style={{ padding: "0.4rem 1rem" }}>Send</button>
      </div>
      {pending.length > 0 && (
        <section style={{ marginTop: "2rem" }}>
          <h3>Pending Tasks</h3>
          {pending.map((t) => (
            <div key={t.id} style={{ border: "1px solid #f99", padding: "0.5rem", marginBottom: "0.5rem" }}>
              <p>{t.description}</p>
              <button onClick={() => approveTask(t.id)}>Approve</button>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
