"use client";
import { useState } from "react";

interface SearchResult {
  media_id: string;
  t0: number;
  t1: number;
  text: string;
}

interface SearchResponse {
  query: string;
  results: SearchResult[];
}

export default function Home() {
  const [q, setQ] = useState<string>("");
  const [res, setRes] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API}/search?q=${encodeURIComponent(q)}`);
      if (!r.ok) {
        throw new Error(`Request failed with status ${r.status}`);
      }
      const data: SearchResponse = await r.json();
      setRes(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      setRes(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 760, margin: "40px auto", padding: 20 }}>
      <h1>OpenWords</h1>
      <p>Search transcripts & jump to timestamps (skeleton).</p>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search…"
          style={{ flex: 1, padding: 8 }}
        />
        <button onClick={run} disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
      </div>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <pre
        style={{
          marginTop: 20,
          background: "#111",
          color: "#0f0",
          padding: 12,
          borderRadius: 6,
        }}
      >
        {loading
          ? "Loading..."
          : res
          ? JSON.stringify(res, null, 2)
          : "No results yet."}
      </pre>
    </main>
  );
}