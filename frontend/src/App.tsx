import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { MessageSquare, Calendar, CheckSquare, BrainCircuit, Palette } from 'lucide-react';
import './index.css';

import { ChatView } from './components/chat/ChatView';

import { StudyPlanView } from './components/studyplan/StudyPlanView';

import { FlashcardsView } from './components/flashcards/FlashcardsView';

import { MindmapView } from './components/mindmap/MindmapView';

function App() {
  type Theme = 'midnight-aurora' | 'forest-deep' | 'solar-flare' | 'light-frost';
  const themes: Theme[] = ['midnight-aurora', 'forest-deep', 'solar-flare', 'light-frost'];
  const themeLabels: Record<Theme, string> = {
    'midnight-aurora': '🌌 Midnight Aurora',
    'forest-deep': '🌲 Forest Deep',
    'solar-flare': '🔥 Solar Flare',
    'light-frost': '❄️ Light Frost',
  };

  const [theme, setTheme] = useState<Theme>(
    (localStorage.getItem('app-theme') as Theme) || 'midnight-aurora'
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('app-theme', theme);
  }, [theme]);

  const cycleTheme = () => {
    const idx = themes.indexOf(theme);
    setTheme(themes[(idx + 1) % themes.length]);
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

          <div className="sidebar-header" style={{ borderBottom: 'none', borderTop: 'var(--border)' }}>
            <button onClick={cycleTheme} className="nav-item" style={{ width: '100%', background: 'transparent', border: 'none', textAlign: 'left', cursor: 'pointer', color: 'inherit' }}>
              <Palette size={20} />
              {themeLabels[theme]}
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
