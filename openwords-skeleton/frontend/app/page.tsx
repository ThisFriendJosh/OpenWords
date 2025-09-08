'use client';
import { useState } from 'react';

export default function Home() {
  const [q, setQ] = useState('');
  const [res, setRes] = useState<any>(null);
  const API = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

  const run = async () => {
    const r = await fetch(`${API}/search?q=${encodeURIComponent(q)}`);
    setRes(await r.json());
  };

  return (
    <main style={{ maxWidth: 760, margin: '40px auto', padding: 20 }}>
      <h1>OpenWords</h1>
      <p>Search transcripts & jump to timestamps (skeleton).</p>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Search…"
          style={{ flex: 1, padding: 8 }}
        />
        <button onClick={run}>Search</button>
      </div>
      <pre style={{ marginTop: 20, background: '#111', color: '#0f0', padding: 12, borderRadius: 6 }}>
        {res ? JSON.stringify(res, null, 2) : 'No results yet.'}
      </pre>
    </main>
  );
}