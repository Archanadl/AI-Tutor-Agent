import React, { useState } from 'react';
import { Loader2 } from 'lucide-react';

export const FlashcardsView = () => {
  const [activeTab, setActiveTab] = useState<'flashcards' | 'quiz'>('flashcards');

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div className="hero">
        <div className="eyebrow">Interactive Learning</div>
        <h1>Master any topic with <span className="grad-text">Flashcards & Quizzes</span></h1>
        <p>Generate AI-powered flashcards with spaced repetition or test your knowledge with interactive quizzes.</p>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <button 
          className={`btn ${activeTab === 'flashcards' ? 'btn-primary' : ''}`}
          onClick={() => setActiveTab('flashcards')}
        >
          📇 Flashcards
        </button>
        <button 
          className={`btn ${activeTab === 'quiz' ? 'btn-primary' : ''}`}
          onClick={() => setActiveTab('quiz')}
        >
          📝 Quizzes
        </button>
      </div>

      {activeTab === 'flashcards' ? <FlashcardsComponent /> : <QuizComponent />}
    </div>
  );
};

// ---------------------------------------------------------
// FLASHCARDS COMPONENT
// ---------------------------------------------------------

interface Flashcard {
  front: string;
  back: string;
}

const FlashcardsComponent = () => {
  const [topic, setTopic] = useState('Machine Learning basics');
  const [count, setCount] = useState(5);
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [flipped, setFlipped] = useState(false);

  const generateCards = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setCards([]);
    setCurrentIdx(0);
    setFlipped(false);
    
    try {
      const res = await fetch('/api/flashcards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, count }),
      });
      const data = await res.json();
      setCards(data.flashcards);
    } catch (err) {
      console.error(err);
      alert('Error generating flashcards');
    } finally {
      setIsLoading(false);
    }
  };

  const rateCard = async (quality: number) => {
    setFlipped(false);
    
    try {
      // In a real app we'd save this to a user profile database, 
      // but for now we just call the API to get the SM-2 calc and log it
      await fetch('/api/flashcards/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quality, previous_interval: 0, previous_repetitions: 0, previous_ease_factor: 2.5 }),
      });
      
      setCurrentIdx(prev => prev + 1);
    } catch (err) {
      console.error(err);
      setCurrentIdx(prev => prev + 1);
    }
  };

  if (isLoading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <Loader2 className="lucide-spin" size={32} style={{ margin: '0 auto 1rem', color: 'var(--primary)' }} />
        <p>Generating high-quality flashcards...</p>
      </div>
    );
  }

  if (cards.length > 0 && currentIdx < cards.length) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <p style={{ color: 'var(--muted)', marginBottom: '1rem' }}>Card {currentIdx + 1} of {cards.length}</p>
        
        {/* CSS Flip Card */}
        <div style={{ perspective: '1200px', width: '100%', maxWidth: '600px', height: '320px', cursor: 'pointer', marginBottom: '2rem' }} onClick={() => setFlipped(!flipped)}>
          <div style={{
            position: 'relative', width: '100%', height: '100%', transition: 'transform 0.7s',
            transformStyle: 'preserve-3d', transform: flipped ? 'rotateY(180deg)' : ''
          }}>
            {/* Front */}
            <div style={{
              position: 'absolute', width: '100%', height: '100%', backfaceVisibility: 'hidden',
              background: 'linear-gradient(160deg, color-mix(in srgb, var(--primary) 10%, var(--surface)), var(--surface) 60%)',
              border: '1px solid var(--border)', borderRadius: '24px', display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', padding: '32px', textAlign: 'center',
              boxShadow: '0 12px 40px -18px rgba(0,0,0,0.25)'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '16px', opacity: 0.7 }}>❓</div>
              <div style={{ fontSize: '0.7rem', letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '12px' }}>Question</div>
              <div style={{ fontFamily: "'Sora', sans-serif", fontSize: '1.2rem', fontWeight: 600 }}>{cards[currentIdx].front}</div>
            </div>
            
            {/* Back */}
            <div style={{
              position: 'absolute', width: '100%', height: '100%', backfaceVisibility: 'hidden',
              background: 'linear-gradient(160deg, color-mix(in srgb, var(--primary-2) 12%, var(--surface)), var(--surface) 60%)',
              border: '1px solid var(--border)', borderRadius: '24px', display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', padding: '32px', textAlign: 'center',
              boxShadow: '0 12px 40px -18px rgba(0,0,0,0.25)',
              transform: 'rotateY(180deg)'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '16px', opacity: 0.7 }}>💡</div>
              <div style={{ fontSize: '0.7rem', letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '12px' }}>Answer</div>
              <div style={{ fontFamily: "'Sora', sans-serif", fontSize: '1.15rem', fontWeight: 500 }}>{cards[currentIdx].back}</div>
            </div>
          </div>
        </div>

        {flipped && (
          <div style={{ width: '100%', maxWidth: '600px', textAlign: 'center' }}>
            <p style={{ color: 'var(--muted)', fontSize: '0.88rem', marginBottom: '1rem' }}>How well did you know this?</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '8px' }}>
              <button className="btn" onClick={(e) => { e.stopPropagation(); rateCard(0); }} title="Blackout">😵 0</button>
              <button className="btn" onClick={(e) => { e.stopPropagation(); rateCard(1); }} title="Barely">😰 1</button>
              <button className="btn" onClick={(e) => { e.stopPropagation(); rateCard(2); }} title="Hard">😐 2</button>
              <button className="btn" onClick={(e) => { e.stopPropagation(); rateCard(3); }} title="OK">🙂 3</button>
              <button className="btn" onClick={(e) => { e.stopPropagation(); rateCard(4); }} title="Good">😊 4</button>
              <button className="btn" onClick={(e) => { e.stopPropagation(); rateCard(5); }} title="Perfect">🤩 5</button>
            </div>
          </div>
        )}
      </div>
    );
  }

  if (cards.length > 0 && currentIdx >= cards.length) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎉</div>
        <h2>All cards reviewed!</h2>
        <p style={{ color: 'var(--muted)', marginBottom: '2rem' }}>Great work! Generate more cards or revisit this set.</p>
        <button className="btn btn-primary" onClick={() => { setCards([]); setCurrentIdx(0); }}>Start Over</button>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="mb-4">🛠️ Generate New Flashcards</h3>
      <form onSubmit={generateCards} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Topic</label>
          <input className="input" value={topic} onChange={(e) => setTopic(e.target.value)} />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Number of Cards</label>
          <input type="number" min="1" max="20" className="input" value={count} onChange={(e) => setCount(Number(e.target.value))} />
        </div>
        <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem' }}>Generate Cards</button>
      </form>
    </div>
  );
};


// ---------------------------------------------------------
// QUIZ COMPONENT
// ---------------------------------------------------------

interface QuizItem {
  q: string;
  options: string[];
  answer: string;
  why: string;
}

const QuizComponent = () => {
  const [topic, setTopic] = useState('Computer Networks');
  const [difficulty, setDifficulty] = useState('Medium');
  const [count, setCount] = useState(5);
  
  const [items, setItems] = useState<QuizItem[]>([]);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const generateQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setItems([]);
    setSelectedAnswers({});
    setIsSubmitted(false);
    
    try {
      const res = await fetch('/api/quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, difficulty, count }),
      });
      const data = await res.json();
      setItems(data.quiz);
    } catch (err) {
      console.error(err);
      alert('Error generating quiz');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (idx: number, opt: string) => {
    if (isSubmitted) return;
    setSelectedAnswers(prev => ({ ...prev, [idx]: opt }));
  };

  const submitQuiz = () => {
    if (Object.keys(selectedAnswers).length < items.length) {
      alert("Please answer all questions before submitting.");
      return;
    }
    setIsSubmitted(true);
  };

  if (isLoading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <Loader2 className="lucide-spin" size={32} style={{ margin: '0 auto 1rem', color: 'var(--primary)' }} />
        <p>Agent building quiz questions...</p>
      </div>
    );
  }

  if (items.length > 0) {
    let score = 0;
    if (isSubmitted) {
      score = items.reduce((acc, item, i) => acc + (selectedAnswers[i] === item.answer ? 1 : 0), 0);
    }

    return (
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h3>📝 {topic}</h3>
            <p style={{ color: 'var(--muted)' }}>{difficulty} • {items.length} questions</p>
          </div>
          <button className="btn" onClick={() => setItems([])}>← Back to settings</button>
        </div>

        {isSubmitted && (
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>🎯</div>
              <div style={{ color: 'var(--muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>Score</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{score}/{items.length}</div>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>📊</div>
              <div style={{ color: 'var(--muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>Percentage</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{Math.round((score / items.length) * 100)}%</div>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>🏆</div>
              <div style={{ color: 'var(--muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>Verdict</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{score / items.length >= 0.7 ? 'Strong' : 'Review'}</div>
            </div>
          </div>
        )}

        {items.map((item, idx) => (
          <div key={idx} className="mb-8">
            <p style={{ fontWeight: 600, marginBottom: '1rem' }}>{idx + 1}. {item.q}</p>
            <div className="grid grid-cols-2 gap-4">
              {item.options.map((opt, optIdx) => {
                const isSelected = selectedAnswers[idx] === opt;
                const isCorrect = isSubmitted && opt === item.answer;
                const isWrong = isSubmitted && isSelected && opt !== item.answer;
                
                let borderColor = 'var(--border)';
                let bg = 'var(--surface)';
                
                if (isSelected) { borderColor = 'var(--primary)'; bg = 'var(--surface-strong)'; }
                if (isCorrect) { borderColor = 'var(--primary)'; bg = 'color-mix(in srgb, var(--primary) 20%, var(--surface))'; }
                if (isWrong) { borderColor = 'var(--danger)'; bg = 'color-mix(in srgb, var(--danger) 20%, var(--surface))'; }

                return (
                  <button 
                    key={optIdx} 
                    className="card" 
                    style={{ 
                      textAlign: 'left', 
                      cursor: isSubmitted ? 'default' : 'pointer',
                      border: `1px solid ${borderColor}`,
                      background: bg,
                      padding: '1rem'
                    }}
                    onClick={() => handleSelect(idx, opt)}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
            {isSubmitted && (
              <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--surface-strong)', borderRadius: '12px', borderLeft: '4px solid var(--primary-2)' }}>
                <p style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>{item.why}</p>
              </div>
            )}
          </div>
        ))}

        {!isSubmitted && (
          <button className="btn btn-primary" style={{ width: '100%', padding: '1rem' }} onClick={submitQuiz}>
            ✅ Submit Quiz
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="mb-4">🛠️ Quiz Settings</h3>
      <form onSubmit={generateQuiz} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Topic</label>
            <input className="input" value={topic} onChange={(e) => setTopic(e.target.value)} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Difficulty</label>
            <select className="input" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              <option>Easy</option>
              <option>Medium</option>
              <option>Hard</option>
            </select>
          </div>
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--muted)' }}>Number of Questions: {count}</label>
          <input type="range" min="3" max="15" style={{ width: '100%' }} value={count} onChange={(e) => setCount(Number(e.target.value))} />
        </div>
        <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem' }}>Generate Quiz</button>
      </form>
    </div>
  );
};
