import React, { useState, useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import { Loader2 } from 'lucide-react';

export const MindmapView = () => {
  const [topic, setTopic] = useState('Document Summary');
  const [mindmapCode, setMindmapCode] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showCode, setShowCode] = useState(false);
  
  const mermaidRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    mermaid.initialize({ startOnLoad: true, theme: 'dark' });
  }, []);

  useEffect(() => {
    if (mindmapCode && mermaidRef.current) {
      mermaidRef.current.removeAttribute('data-processed');
      mermaid.contentLoaded();
    }
  }, [mindmapCode]);

  const generateMindmap = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim() || isLoading) return;
    
    setIsLoading(true);
    setMindmapCode(null);
    
    try {
      const res = await fetch('/api/mindmap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, document_id: null }),
      });
      const data = await res.json();
      setMindmapCode(data.code);
    } catch (err) {
      console.error(err);
      alert('Error generating mindmap');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div className="hero">
        <div className="eyebrow">Visualize</div>
        <h1>Mind <span className="grad-text">Maps</span></h1>
        <p>Generate interactive concept maps from your study material or custom topics.</p>
      </div>

      <div className="card mb-8">
        <form onSubmit={generateMindmap} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Topic or Concept</label>
            <input 
              type="text" 
              className="input" 
              placeholder="What should the mind map be about?" 
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={isLoading}>
            Generate Mind Map
          </button>
        </form>
      </div>

      {isLoading && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <Loader2 className="animate-spin" size={32} style={{ margin: '0 auto 1rem', color: 'var(--primary)' }} />
          <p>Agent generating mind map...</p>
        </div>
      )}

      {mindmapCode && !isLoading && (
        <div>
          <h3>🗺️ {topic}</h3>
          <div className="card" style={{ marginTop: '1rem', overflowX: 'auto', background: '#0b1020', border: '1px solid var(--primary-2)' }}>
            <div className="mermaid" ref={mermaidRef}>
              {mindmapCode}
            </div>
          </div>
          
          <div style={{ marginTop: '1rem' }}>
            <button className="btn" onClick={() => setShowCode(!showCode)}>
              📄 {showCode ? 'Hide' : 'Show'} Mermaid Source Code
            </button>
            {showCode && (
              <pre style={{ marginTop: '1rem', padding: '1rem', background: 'var(--input-bg)', borderRadius: '12px', border: '1px solid var(--border)', overflowX: 'auto' }}>
                <code>{mindmapCode}</code>
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
