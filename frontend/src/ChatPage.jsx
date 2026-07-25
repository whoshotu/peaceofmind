import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

const API_BASE = "/api";

export default function ChatPage() {
  const [fans, setFans] = useState([]);
  const [selectedFan, setSelectedFan] = useState(null);
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [showNewFan, setShowNewFan] = useState(false);
  const [newFanName, setNewFanName] = useState("");
  const [newFanTier, setNewFanTier] = useState("free");
  const [newFanNotes, setNewFanNotes] = useState("");
  const logEnd = useRef(null);

  const fetchFans = async () => {
    try {
      const res = await axios.get(`${API_BASE}/fans`);
      setFans(res.data.fans || []);
    } catch {}
  };

  useEffect(() => { fetchFans(); }, []);

  useEffect(() => {
    logEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatLog]);

  const selectFan = (fan) => {
    setSelectedFan(fan);
    setChatLog([]);
  };

  const createFan = async () => {
    if (!newFanName.trim()) return;
    const res = await axios.post(`${API_BASE}/fans`, {
      name: newFanName,
      tier: newFanTier,
      notes: newFanNotes,
    });
    setNewFanName("");
    setNewFanNotes("");
    setShowNewFan(false);
    fetchFans();
    setSelectedFan(res.data);
    setChatLog([]);
  };

  const sendMessage = async () => {
    if (!message || !selectedFan) return;
    const userMsg = message;
    setChatLog((c) => [...c, { from: "user", text: userMsg }]);
    setMessage("");
    try {
      const resp = await axios.post(`${API_BASE}/fans/${selectedFan.id}/chat`, {
        message: userMsg,
      });
      const reply = resp.data;
      setChatLog((c) => [...c, { from: "agent", text: reply.content }]);
    } catch {
      setChatLog((c) => [...c, { from: "agent", text: "(Error getting reply)" }]);
    }
  };

  const tierBadge = (tier) => {
    return { free: "#888", basic: "#1976d2", premium: "#f57c00", vip: "#d32f2f" }[tier] || "#888";
  };

  return (
    <div style={{ display: "flex", gap: "1rem" }}>
      {/* Fan sidebar */}
      <div style={{ width: 240, flexShrink: 0 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
          <strong>Fans</strong>
          <button onClick={() => setShowNewFan(true)} style={{ background: "#1976d2", color: "#fff", border: "none", borderRadius: 4, padding: "0.2rem 0.6rem", cursor: "pointer" }}>+ New</button>
        </div>

        {showNewFan && (
          <div style={{ border: "1px solid #ddd", padding: "0.5rem", marginBottom: "0.5rem", borderRadius: 4 }}>
            <input placeholder="Fan name" value={newFanName} onChange={(e) => setNewFanName(e.target.value)} style={{ width: "100%", marginBottom: "0.3rem", padding: "0.2rem" }} />
            <select value={newFanTier} onChange={(e) => setNewFanTier(e.target.value)} style={{ width: "100%", marginBottom: "0.3rem", padding: "0.2rem" }}>
              <option value="free">Free</option>
              <option value="basic">Basic</option>
              <option value="premium">Premium</option>
              <option value="vip">VIP</option>
            </select>
            <input placeholder="Notes (optional)" value={newFanNotes} onChange={(e) => setNewFanNotes(e.target.value)} style={{ width: "100%", marginBottom: "0.3rem", padding: "0.2rem" }} />
            <div style={{ display: "flex", gap: "0.3rem" }}>
              <button onClick={createFan} style={{ flex: 1, background: "#1976d2", color: "#fff", border: "none", borderRadius: 4, padding: "0.2rem", cursor: "pointer" }}>Save</button>
              <button onClick={() => setShowNewFan(false)} style={{ flex: 1, background: "#ddd", border: "none", borderRadius: 4, padding: "0.2rem", cursor: "pointer" }}>Cancel</button>
            </div>
          </div>
        )}

        {fans.map((f) => (
          <div
            key={f.id}
            onClick={() => selectFan(f)}
            style={{
              padding: "0.4rem 0.5rem",
              marginBottom: "0.2rem",
              borderRadius: 4,
              cursor: "pointer",
              background: selectedFan?.id === f.id ? "#e3f2fd" : "transparent",
              borderLeft: `3px solid ${tierBadge(f.tier)}`,
            }}
          >
            <div style={{ fontWeight: 500 }}>{f.name}</div>
            <div style={{ fontSize: "0.75rem", color: tierBadge(f.tier) }}>{f.tier}</div>
          </div>
        ))}

        {selectedFan && (
          <div style={{ marginTop: "1rem", fontSize: "0.85rem", color: "#666", borderTop: "1px solid #eee", paddingTop: "0.5rem" }}>
            <strong>Context</strong>
            <p style={{ margin: "0.2rem 0" }}>Tier: {selectedFan.tier}</p>
            {selectedFan.notes && <p style={{ margin: "0.2rem 0" }}>Notes: {selectedFan.notes}</p>}
          </div>
        )}
      </div>

      {/* Chat area */}
      <div style={{ flex: 1 }}>
        {!selectedFan ? (
          <p style={{ color: "#888" }}>Select a fan from the sidebar, or create a new one.</p>
        ) : (
          <>
            <div style={{ border: "1px solid #ddd", padding: "0.5rem", minHeight: 350, marginBottom: "0.5rem", overflowY: "auto" }}>
              {chatLog.map((m, i) => (
                <div key={i} style={{ marginBottom: "0.5rem", textAlign: m.from === "user" ? "right" : "left" }}>
                  <span style={{
                    display: "inline-block",
                    background: m.from === "user" ? "#e3f2fd" : "#f5f5f5",
                    padding: "0.3rem 0.6rem",
                    borderRadius: 8,
                    maxWidth: "80%",
                  }}>
                    <strong>{m.from}:</strong> {m.text}
                  </span>
                </div>
              ))}
              <div ref={logEnd} />
            </div>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <input
                type="text"
                placeholder={`Reply to ${selectedFan.name}...`}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                style={{ flex: 1, padding: "0.4rem" }}
              />
              <button onClick={sendMessage} style={{ padding: "0.4rem 1rem" }}>Send</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
