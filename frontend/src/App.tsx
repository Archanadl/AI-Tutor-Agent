import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { MessageSquare, Calendar, CheckSquare, BrainCircuit, Settings, Palette } from 'lucide-react';
import './index.css';

import { ChatView } from './components/chat/ChatView';

import { StudyPlanView } from './components/studyplan/StudyPlanView';

import { FlashcardsView } from './components/flashcards/FlashcardsView';

import { MindmapView } from './components/mindmap/MindmapView';

function App() {
  const [theme, setTheme] = useState<'dark' | 'light' | 'solar-flare'>(
    (localStorage.getItem('app-theme') as any) || 'dark'
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('app-theme', theme);
  }, [theme]);

  const cycleTheme = () => {
    if (theme === 'dark') setTheme('light');
    else if (theme === 'light') setTheme('solar-flare');
    else setTheme('dark');
  };

  return (
    <BrowserRouter>
      <div className="app-container">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <h1 style={{ marginBottom: 0 }}>🎓 AI Tutor</h1>
            <p>Multi-agent RAG learning assistant</p>
          </div>
          
          <div className="nav-links">
            <NavLink to="/chat" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <MessageSquare size={20} />
              AI Tutor
            </NavLink>
            <NavLink to="/plan" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <Calendar size={20} />
              Study Plan & Progress
            </NavLink>
            <NavLink to="/flashcards" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <CheckSquare size={20} />
              Flashcards & Quizzes
            </NavLink>
            <NavLink to="/mindmap" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <BrainCircuit size={20} />
              Mindmap
            </NavLink>
          </div>

          <div className="sidebar-header" style={{ borderBottom: 'none', borderTop: '1px solid var(--border)' }}>
            <button onClick={cycleTheme} className="nav-item" style={{ width: '100%', background: 'transparent', border: 'none', textAlign: 'left', cursor: 'pointer', color: 'inherit' }}>
              <Palette size={20} />
              Theme: {theme === 'dark' ? 'Dark' : theme === 'light' ? 'Light' : 'Solar Flare'}
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/chat" element={<ChatView />} />
            <Route path="/plan" element={<StudyPlanView />} />
            <Route path="/flashcards" element={<FlashcardsView />} />
            <Route path="/mindmap" element={<MindmapView />} />
            <Route path="*" element={<Navigate to="/chat" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
