import React from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { MessageSquare, Calendar, CheckSquare, BrainCircuit, Settings } from 'lucide-react';
import './index.css';

import { ChatView } from './components/chat/ChatView';

import { StudyPlanView } from './components/studyplan/StudyPlanView';

import { FlashcardsView } from './components/flashcards/FlashcardsView';

import { MindmapView } from './components/mindmap/MindmapView';

function App() {
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
            <button className="nav-item" style={{ width: '100%', background: 'transparent', border: 'none', textAlign: 'left', cursor: 'pointer' }}>
              <Settings size={20} />
              Settings
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
