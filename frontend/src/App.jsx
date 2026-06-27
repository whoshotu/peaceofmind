import React, { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = "/api"; // assumes API Gateway is proxied in dev via docker-compose

function App() {
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [pending, setPending] = useState([]);

  useEffect(() => {
    // fetch pending tasks (placeholder empty list)
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
    const userMsg = { role: "user", content: message };
    setChatLog((c) => [...c, { from: "user", text: message }]);
    setMessage("");
    const resp = await axios.post(`${API_BASE}/chat`, { messages: [userMsg] });
    const reply = resp.data;
    setChatLog((c) => [...c, { from: "agent", text: reply.content || JSON.stringify(reply) }]);
  };

  const approveTask = async (taskId) => {
    await axios.post(`${API_BASE}/admin/approve`, { task_id: taskId });
    setPending((p) => p.filter((t) => t.id !== taskId));
  };

  return (
    <div style={{ maxWidth: 800, margin: "auto", padding: "1rem" }}>
      <h2>peaceofmind – Agent Society Demo</h2>
      <div style={{ border: "1px solid #ddd", padding: "0.5rem", minHeight: 200 }}>
        {chatLog.map((m, i) => (
          <div key={i} style={{ marginBottom: "0.5rem" }}>
            <strong>{m.from}:</strong> {m.text}
          </div>
        ))}
      </div>
      <div style={{ marginTop: "1rem" }}>
        <input
          type="text"
          placeholder="Ask a question..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={{ width: "80%" }}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
      {pending.length > 0 && (
        <section style={{ marginTop: "2rem" }}>
          <h3>Pending Human‑In‑The‑Loop Tasks</h3>
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

export default App;
