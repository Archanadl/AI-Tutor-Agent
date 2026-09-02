import React, { useState } from 'react';
import { Loader2 } from 'lucide-react';

export const StudyPlanView = () => {
  const [activeTab, setActiveTab] = useState<'plan' | 'progress'>('plan');

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div className="hero">
        <div className="eyebrow">Plan & Track</div>
        <h1>Your personalized study <span className="grad-text">dashboard</span></h1>
        <p>Create study plans, track your progress, and identify weak areas — all in one place.</p>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <button 
          className={`btn ${activeTab === 'plan' ? 'btn-primary' : ''}`}
          onClick={() => setActiveTab('plan')}
        >
          📅 Study Plan
        </button>
        <button 
          className={`btn ${activeTab === 'progress' ? 'btn-primary' : ''}`}
          onClick={() => setActiveTab('progress')}
        >
          📈 Progress
        </button>
      </div>

      {activeTab === 'plan' ? <StudyPlanComponent /> : <ProgressComponent />}
    </div>
  );
};

// ---------------------------------------------------------
// STUDY PLAN COMPONENT
// ---------------------------------------------------------

const StudyPlanComponent = () => {
  const [goal, setGoal] = useState('');
  const [level, setLevel] = useState('Intermediate');
  const [topics, setTopics] = useState('');
  const [hours, setHours] = useState(3.0);
  const [sessions, setSessions] = useState(10);
  const [planType, setPlanType] = useState('Learning');
  const [examDate, setExamDate] = useState('');
  
  const [plan, setPlan] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const generatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setPlan(null);
    
    try {
      const res = await fetch('/api/study-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal,
          current_level: level,
          topics: topics.split(',').map(t => t.trim()),
          daily_hours: hours,
          duration_days: sessions,
          plan_type: planType === 'Learning' ? 'learning' : 'exam_preparation',
          exam_date: planType === 'Exam Preparation' ? examDate : null
        }),
      });
      const data = await res.json();
      setPlan(data);
    } catch (err) {
      console.error(err);
      alert('Error generating study plan');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSessionAction = async (sessionNumber: number, action: 'start' | 'complete') => {
    try {
      const res = await fetch(`/api/study-plan/session/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan, session_number: sessionNumber }),
      });
      const updatedPlan = await res.json();
      setPlan(updatedPlan);
    } catch (err) {
      console.error(err);
      alert(`Error trying to ${action} session`);
    }
  };

  if (plan && plan.study_sessions) {
    const studySessions = plan.study_sessions;
    const completed = studySessions.filter((s: any) => s.status === 'completed').length;
    const progress = Math.round((completed / studySessions.length) * 100);

    return (
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h3>📖 Your Study Plan</h3>
          <button className="btn" onClick={() => setPlan(null)}>← New Plan</button>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="card">
            <div style={{ color: 'var(--muted)', fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '8px' }}>Total Sessions</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{studySessions.length}</div>
          </div>
          <div className="card">
            <div style={{ color: 'var(--muted)', fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '8px' }}>Completed</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>{completed}</div>
          </div>
          <div className="card">
            <div style={{ color: 'var(--muted)', fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '8px' }}>Remaining</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{studySessions.length - completed}</div>
          </div>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', color: 'var(--muted)', fontSize: '0.9rem' }}>
            <span>Progress</span>
            <span>{progress}%</span>
          </div>
          <div style={{ height: '12px', background: 'var(--surface-strong)', borderRadius: '99px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${progress}%`, background: 'linear-gradient(90deg, var(--primary), var(--primary-2))' }} />
          </div>
        </div>

        <div style={{ position: 'relative', borderLeft: '2px solid var(--border)', marginLeft: '16px', paddingLeft: '32px' }}>
          {studySessions.map((session: any, idx: number) => {
            const isCompleted = session.status === 'completed';
            const isInProgress = session.status === 'in_progress';
            const isPending = session.status === 'pending';
            
            return (
              <div key={idx} className="card" style={{ marginBottom: '1.5rem', position: 'relative' }}>
                <div style={{ 
                  position: 'absolute', left: '-44px', top: '24px', width: '20px', height: '20px', 
                  borderRadius: '50%', background: isCompleted ? 'var(--primary)' : 'var(--surface-strong)',
                  border: `4px solid var(--bg)`, zIndex: 2
                }} />
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                  <div>
                    <h4 style={{ marginBottom: '4px' }}>Session {session.session}</h4>
                    <span style={{ 
                      fontSize: '0.75rem', padding: '2px 8px', borderRadius: '99px',
                      background: isCompleted ? 'color-mix(in srgb, var(--primary) 20%, transparent)' : 'var(--surface-strong)',
                      color: isCompleted ? 'var(--primary)' : 'var(--muted)'
                    }}>
                      {session.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  
                  {isPending && (
                    <button className="btn" onClick={() => handleSessionAction(session.session, 'start')}>
                      ▶️ Start Session
                    </button>
                  )}
                  {isInProgress && (
                    <button className="btn btn-primary" onClick={() => handleSessionAction(session.session, 'complete')}>
                      ✅ Complete Session
                    </button>
                  )}
                </div>

                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {session.tasks.map((task: any, tIdx: number) => (
                    <li key={tIdx} style={{ padding: '0.75rem', background: 'var(--surface-strong)', borderRadius: '12px', marginBottom: '0.5rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <strong>{task.topic}</strong>
                        <span style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>⏱️ {task.duration_minutes} min</span>
                      </div>
                      <p style={{ color: 'var(--muted)', fontSize: '0.9rem', marginTop: '4px' }}>{task.description}</p>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="mb-4">🎯 Create your personalized study plan</h3>
      <form onSubmit={generatePlan} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Plan type</label>
            <select className="input" value={planType} onChange={(e) => setPlanType(e.target.value)}>
              <option>Learning</option>
              <option>Exam Preparation</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Current level</label>
            <select className="input" value={level} onChange={(e) => setLevel(e.target.value)}>
              <option>Beginner</option>
              <option>Intermediate</option>
              <option>Advanced</option>
            </select>
          </div>
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>What do you want to achieve?</label>
          <input className="input" placeholder="e.g. Learn DSA for placement preparation" value={goal} onChange={(e) => setGoal(e.target.value)} required />
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Topics (comma separated)</label>
          <input className="input" placeholder="e.g. Arrays, Strings, Recursion" value={topics} onChange={(e) => setTopics(e.target.value)} required />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Study time per session (hours): {hours}</label>
            <input type="range" min="1" max="8" step="0.5" style={{ width: '100%' }} value={hours} onChange={(e) => setHours(Number(e.target.value))} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Number of sessions</label>
            <input type="number" min="1" max="365" className="input" value={sessions} onChange={(e) => setSessions(Number(e.target.value))} />
          </div>
        </div>

        {planType === 'Exam Preparation' && (
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Exam Date</label>
            <input type="date" className="input" value={examDate} onChange={(e) => setExamDate(e.target.value)} required />
          </div>
        )}

        <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem' }} disabled={isLoading}>
          {isLoading ? <Loader2 className="lucide-spin" size={18} /> : '✨ Generate Personalized Study Plan'}
        </button>
      </form>
    </div>
  );
};


// ---------------------------------------------------------
// PROGRESS COMPONENT
// ---------------------------------------------------------

const ProgressComponent = () => {
  return (
    <div>
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="card">
          <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>📚</div>
          <div style={{ color: 'var(--muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>Topics Studied</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>0</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>📝</div>
          <div style={{ color: 'var(--muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>Quizzes Taken</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>0</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>🔥</div>
          <div style={{ color: 'var(--muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>Study Streak</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>0 days</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '2rem', textAlign: 'center', padding: '3rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>No Data Available Yet</h3>
        <p style={{ color: 'var(--muted)' }}>Complete quizzes and study sessions to unlock your progress dashboard, weak topics analysis, and revision recommendations.</p>
      </div>
    </div>
  );
};
