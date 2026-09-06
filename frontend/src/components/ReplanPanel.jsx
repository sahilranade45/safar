import { useState } from 'react';

export default function ReplanPanel({ originalRequest, existingPlan, onReplan, isLoading }) {
  const [modification, setModification] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!modification.trim()) return;
    onReplan({
      original_request: originalRequest,
      modification: modification.trim(),
      existing_plan: existingPlan,
    });
    setModification('');
  };

  const suggestions = [
    'Reduce the budget to ₹15,000',
    'Add more cultural activities',
    'Remove expensive activities',
    'I prefer more outdoor adventures',
    'Add beach activities',
    'Make it more relaxed with fewer activities',
  ];

  return (
    <div className="replan-panel glass-card fade-in">
      <h3 style={{ marginBottom: 'var(--space-sm)' }}>
        <span className="section-icon">🔄</span> Modify Your Plan
      </h3>
      <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', marginBottom: 'var(--space-md)' }}>
        Not quite right? Tell our AI team what to change.
      </p>

      {/* Quick suggestions */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-sm)', marginBottom: 'var(--space-md)' }}>
        {suggestions.map((s, i) => (
          <button
            key={i}
            className="interest-tag"
            onClick={() => setModification(s)}
            disabled={isLoading}
            type="button"
          >
            {s}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="replan-input-group">
          <input
            type="text"
            className="form-input"
            placeholder="e.g., 'I want more food experiences' or 'Cut the budget in half'"
            value={modification}
            onChange={e => setModification(e.target.value)}
            disabled={isLoading}
            id="replan-input"
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading || !modification.trim()}
            id="replan-btn"
          >
            {isLoading ? '🔄 Replanning...' : '🔄 Replan'}
          </button>
        </div>
      </form>
    </div>
  );
}
