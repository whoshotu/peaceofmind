import React, { useState } from "react";
import ChatPage from "./ChatPage";
import MediaLibrary from "./MediaLibrary";

function App() {
  const [page, setPage] = useState("chat");

  return (
    <div style={{ maxWidth: 900, margin: "auto", padding: "1rem" }}>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", borderBottom: "1px solid #ddd", paddingBottom: "0.5rem" }}>
        <h2 style={{ margin: 0, marginRight: "auto" }}>peaceofmind</h2>
        <button
          onClick={() => setPage("chat")}
          style={{ fontWeight: page === "chat" ? "bold" : "normal", background: "none", border: "none", cursor: "pointer", fontSize: "1rem" }}
        >
          Chat
        </button>
        <button
          onClick={() => setPage("media")}
          style={{ fontWeight: page === "media" ? "bold" : "normal", background: "none", border: "none", cursor: "pointer", fontSize: "1rem" }}
        >
          Media Library
        </button>
      </div>

      {page === "chat" ? <ChatPage /> : <MediaLibrary />}
    </div>
  );
}

export default App;
