import { useState } from 'react';

const INTEREST_OPTIONS = [
  'Beaches', 'Culture', 'Food', 'Adventure', 'History',
  'Nature', 'Shopping', 'Nightlife', 'Architecture', 'Photography',
  'Temples', 'Wildlife', 'Trekking', 'Water Sports', 'Art',
];

const TRAVEL_STYLES = [
  { value: 'budget', label: '💰 Budget', desc: 'Maximum experience, minimum spend' },
  { value: 'balanced', label: '⚖️ Balanced', desc: 'Best of both worlds' },
  { value: 'luxury', label: '✨ Luxury', desc: 'Premium comfort & experiences' },
];

export default function TripForm({ onSubmit, isLoading }) {
  const [form, setForm] = useState({
    destination: '',
    days: 3,
    travelers: 2,
    budget: 25000,
    travel_style: 'balanced',
    interests: [],
    food_preference: 'no preference',
    special_requirements: '',
  });

  const updateField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const toggleInterest = (interest) => {
    setForm(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest],
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.destination.trim()) return;
    onSubmit({
      ...form,
      destination: form.destination.trim(),
      interests: form.interests.map(i => i.toLowerCase()),
    });
  };

  return (
    <section className="form-section fade-in">
      <div className="glass-card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            {/* Destination */}
            <div className="form-group full-width">
              <label className="form-label" htmlFor="destination">Where do you want to go?</label>
              <input
                id="destination"
                type="text"
                className="form-input"
                placeholder="e.g., Goa, Manali, Jaipur, Kerala..."
                value={form.destination}
                onChange={e => updateField('destination', e.target.value)}
                required
                disabled={isLoading}
              />
            </div>

            {/* Days */}
            <div className="form-group">
              <label className="form-label" htmlFor="days">Number of Days</label>
              <input
                id="days"
                type="number"
                className="form-input"
                min="1"
                max="30"
                value={form.days}
                onChange={e => updateField('days', parseInt(e.target.value) || 1)}
                disabled={isLoading}
              />
            </div>

            {/* Travelers */}
            <div className="form-group">
              <label className="form-label" htmlFor="travelers">Travelers</label>
              <input
                id="travelers"
                type="number"
                className="form-input"
                min="1"
                max="20"
                value={form.travelers}
                onChange={e => updateField('travelers', parseInt(e.target.value) || 1)}
                disabled={isLoading}
              />
            </div>

            {/* Budget */}
            <div className="form-group">
              <label className="form-label" htmlFor="budget">Budget (₹)</label>
              <input
                id="budget"
                type="number"
                className="form-input"
                min="1000"
                step="1000"
                value={form.budget}
                onChange={e => updateField('budget', parseInt(e.target.value) || 1000)}
                disabled={isLoading}
              />
            </div>

            {/* Food Preference */}
            <div className="form-group">
              <label className="form-label" htmlFor="food_preference">Food Preference</label>
              <select
                id="food_preference"
                className="form-select"
                value={form.food_preference}
                onChange={e => updateField('food_preference', e.target.value)}
                disabled={isLoading}
              >
                <option value="no preference">No Preference</option>
                <option value="vegetarian">Vegetarian</option>
                <option value="vegan">Vegan</option>
                <option value="non-vegetarian">Non-Vegetarian</option>
                <option value="pescatarian">Pescatarian</option>
                <option value="jain">Jain</option>
              </select>
            </div>

            {/* Travel Style */}
            <div className="form-group full-width">
              <label className="form-label">Travel Style</label>
              <div style={{ display: 'flex', gap: 'var(--space-md)', flexWrap: 'wrap' }}>
                {TRAVEL_STYLES.map(style => (
                  <button
                    type="button"
                    key={style.value}
                    className={`interest-tag ${form.travel_style === style.value ? 'active' : ''}`}
                    onClick={() => updateField('travel_style', style.value)}
                    disabled={isLoading}
                    style={{ padding: '12px 20px', fontSize: '0.9rem' }}
                  >
                    <div>{style.label}</div>
                    <div style={{ fontSize: '0.75rem', opacity: 0.7, marginTop: '2px' }}>{style.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Interests */}
            <div className="form-group full-width">
              <label className="form-label">Interests (select all that apply)</label>
              <div className="interest-tags">
                {INTEREST_OPTIONS.map(interest => (
                  <button
                    type="button"
                    key={interest}
                    className={`interest-tag ${form.interests.includes(interest) ? 'active' : ''}`}
                    onClick={() => toggleInterest(interest)}
                    disabled={isLoading}
                  >
                    {interest}
                  </button>
                ))}
              </div>
            </div>

            {/* Special Requirements */}
            <div className="form-group full-width">
              <label className="form-label" htmlFor="special_requirements">Special Requirements (Optional)</label>
              <textarea
                id="special_requirements"
                className="form-textarea"
                placeholder="Any accessibility needs, dietary restrictions, must-visit places..."
                value={form.special_requirements}
                onChange={e => updateField('special_requirements', e.target.value)}
                disabled={isLoading}
              />
            </div>
          </div>

          {/* Submit */}
          <div style={{ textAlign: 'center', marginTop: 'var(--space-xl)' }}>
            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={isLoading || !form.destination.trim()}
              id="plan-trip-btn"
            >
              {isLoading ? '✨ Planning your trip...' : '🚀 Plan My Trip'}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
