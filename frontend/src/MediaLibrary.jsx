import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

const API_BASE = "/api";

export default function MediaLibrary() {
  const [files, setFiles] = useState([]);
  const [search, setSearch] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef();

  const fetchFiles = async (q = "") => {
    try {
      const res = await axios.get(`${API_BASE}/media`, { params: { q } });
      setFiles(res.data.files || []);
    } catch {}
  };

  useEffect(() => { fetchFiles(); }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      await axios.post(`${API_BASE}/media/upload`, fd);
      fetchFiles(search);
    } finally {
      setUploading(false);
      fileRef.current.value = "";
    }
  };

  const handleDelete = async (id) => {
    await axios.delete(`${API_BASE}/media/${id}`);
    setFiles((f) => f.filter((x) => x.id !== id));
  };

  const handleSearch = (e) => {
    const q = e.target.value;
    setSearch(q);
    fetchFiles(q);
  };

  return (
    <div>
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", alignItems: "center" }}>
        <input
          type="text"
          placeholder="Search media..."
          value={search}
          onChange={handleSearch}
          style={{ flex: 1, padding: "0.4rem" }}
        />
        <label style={{ cursor: "pointer", background: "#1976d2", color: "#fff", padding: "0.4rem 1rem", borderRadius: 4 }}>
          {uploading ? "Uploading..." : "+ Upload"}
          <input ref={fileRef} type="file" hidden onChange={handleUpload} accept="image/*,video/*" />
        </label>
      </div>

      {files.length === 0 && <p style={{ color: "#888" }}>No media yet. Upload an image or video.</p>}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "1rem" }}>
        {files.map((f) => (
          <div key={f.id} style={{ border: "1px solid #ddd", borderRadius: 6, overflow: "hidden", position: "relative" }}>
            {f.type === "video" ? (
              <video src={f.url} style={{ width: "100%", height: 160, objectFit: "cover" }} controls />
            ) : (
              <img src={f.url} alt={f.filename} style={{ width: "100%", height: 160, objectFit: "cover" }} />
            )}
            <div style={{ padding: "0.3rem 0.5rem", fontSize: "0.85rem" }}>
              <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{f.filename}</div>
              <button
                onClick={() => handleDelete(f.id)}
                style={{ background: "none", border: "none", color: "#d32f2f", cursor: "pointer", fontSize: "0.8rem", padding: 0 }}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
