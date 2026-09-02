import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Upload, File as FileIcon, Search, CheckCircle2 } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  source?: string;
  confidence?: number;
  source_type?: 'RAG' | 'WEB' | 'NONE';
  trace?: string[];
}

export const ChatView = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setDocumentId(data.name);
        alert(`Document ${data.name} uploaded and indexed successfully.`);
      } else {
        alert(data.detail || data.message || 'Error uploading file');
      }
    } catch (err) {
      console.error(err);
      alert('Network error uploading file');
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          chat_history: messages,
          document_id: documentId,
        }),
      });
      const data = await res.json();
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        source: data.source,
        confidence: data.confidence,
        source_type: data.source_type,
        trace: data.trace,
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, there was an error processing your request.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', maxWidth: '900px', margin: '0 auto' }}>
      
      {/* Header & File Upload */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h2>💬 AI Tutor Chat</h2>
          <p style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>
            {documentId ? `Grounded in ${documentId}` : 'No document loaded — web search fallback active.'}
          </p>
        </div>
        
        <div>
          <input type="file" id="file-upload" accept=".pdf" style={{ display: 'none' }} onChange={handleFileUpload} />
          <label htmlFor="file-upload" className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}>
            <Upload size={16} /> Upload PDF
          </label>
        </div>
      </div>

      {/* Messages Area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius)', border: '1px solid var(--border)', marginBottom: '1rem' }}>
        {messages.length === 0 ? (
          <div className="hero" style={{ textAlign: 'center', margin: '2rem' }}>
            <div className="eyebrow">Welcome</div>
            <h1>How can I help you <span className="grad-text">learn</span> today?</h1>
            <p style={{ margin: '1rem auto' }}>Upload a document or just start asking questions.</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} style={{ 
              marginBottom: '1rem', 
              padding: '1rem', 
              borderRadius: '16px',
              background: msg.role === 'user' ? 'var(--surface-strong)' : 'transparent',
              border: msg.role === 'user' ? '1px solid var(--border)' : 'none'
            }}>
              <div style={{ fontWeight: 600, marginBottom: '0.5rem', color: msg.role === 'user' ? 'var(--text)' : 'var(--primary)' }}>
                {msg.role === 'user' ? '🧑‍🎓 You' : '🎓 Tutor'}
              </div>
              <div style={{ lineHeight: 1.6 }}>
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
              
              {/* Metadata Badges */}
              {msg.role === 'assistant' && msg.source_type && msg.source_type !== 'NONE' && (
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
                  {msg.source_type === 'RAG' ? (
                    <span style={{ fontSize: '0.75rem', background: 'var(--primary)', color: '#000', padding: '2px 8px', borderRadius: '99px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <FileIcon size={12} /> {msg.source}
                    </span>
                  ) : (
                    <span style={{ fontSize: '0.75rem', background: 'var(--primary-2)', color: '#000', padding: '2px 8px', borderRadius: '99px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Search size={12} /> Web Search
                    </span>
                  )}
                  
                  {msg.confidence && (
                    <span style={{ fontSize: '0.75rem', border: '1px solid var(--border)', color: 'var(--muted)', padding: '2px 8px', borderRadius: '99px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <CheckCircle2 size={12} /> Confidence: {msg.confidence}%
                    </span>
                  )}
                </div>
              )}
            </div>
          ))
        )}
        
        {isLoading && (
          <div style={{ padding: '1rem', color: 'var(--muted)' }}>
            🤖 Agent is thinking...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.5rem' }}>
        <input 
          type="text" 
          className="input" 
          placeholder="Ask a question about your study material..." 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
          style={{ flex: 1 }}
        />
        <button type="submit" className="btn btn-primary" disabled={isLoading || !input.trim()}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
};
