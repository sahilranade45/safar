import { useState } from 'react';

const WEATHER_ICONS = {
  'Clear sky': '☀️',
  'Mainly clear': '🌤️',
  'Partly cloudy': '⛅',
  'Overcast': '☁️',
  'Fog': '🌫️',
  'Depositing rime fog': '🌫️',
  'Light drizzle': '🌦️',
  'Moderate drizzle': '🌦️',
  'Dense drizzle': '🌧️',
  'Slight rain': '🌦️',
  'Moderate rain': '🌧️',
  'Heavy rain': '🌧️',
  'Slight snowfall': '🌨️',
  'Moderate snowfall': '❄️',
  'Heavy snowfall': '❄️',
  'Slight rain showers': '🌦️',
  'Moderate rain showers': '🌧️',
  'Violent rain showers': '⛈️',
  'Thunderstorm': '⛈️',
  'Thunderstorm with slight hail': '⛈️',
  'Thunderstorm with heavy hail': '⛈️',
};

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' });
}

export default function TravelPlan({ plan, totalDuration }) {
  const [expandedDays, setExpandedDays] = useState({});

  if (!plan) return null;

  const toggleDay = (dayNum) => {
    setExpandedDays(prev => ({ ...prev, [dayNum]: !prev[dayNum] }));
  };

  const { destination_info, weather_info, budget_breakdown, itinerary, food_recommendations, review_result, travel_tips } = plan;

  return (
    <div className="results-container">
      {/* Header */}
      <div className="result-header fade-in">
        <h2>🗺️ Your {plan.destination} Travel Plan</h2>
        <p>{plan.overview}</p>
      </div>

      {/* Trip Overview Stats */}
      <div className="overview-card fade-in stagger-1">
        <h3><span className="section-icon">📊</span> Trip Overview</h3>
        <div className="overview-stats">
          <div className="stat-item">
            <div className="stat-value">{plan.destination}</div>
            <div className="stat-label">Destination</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{plan.days}</div>
            <div className="stat-label">Days</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{plan.travelers}</div>
            <div className="stat-label">Travelers</div>
          </div>
          <div className="stat-item">
            <div className="stat-value" style={{ textTransform: 'capitalize' }}>{plan.travel_style}</div>
            <div className="stat-label">Style</div>
          </div>
          {budget_breakdown && (
            <div className="stat-item">
              <div className="stat-value">₹{budget_breakdown.total_estimated?.toLocaleString('en-IN')}</div>
              <div className="stat-label">Est. Total</div>
            </div>
          )}
          {totalDuration && (
            <div className="stat-item">
              <div className="stat-value">{totalDuration.toFixed(0)}s</div>
              <div className="stat-label">Planning Time</div>
            </div>
          )}
        </div>
      </div>

      <div className="result-grid">
        {/* Destination Highlights */}
        {destination_info && (
          <div className="glass-card result-section fade-in stagger-2">
            <h3><span className="section-icon">🏛️</span> Destination Highlights</h3>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)', lineHeight: 1.7 }}>
              {destination_info.overview}
            </p>
            {destination_info.best_time_to_visit && (
              <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
                🗓️ Best time to visit: <strong style={{ color: 'var(--color-text-secondary)' }}>{destination_info.best_time_to_visit}</strong>
              </p>
            )}
            {destination_info.attractions?.length > 0 && (
              <div style={{ marginTop: 'var(--space-md)' }}>
                <h4 style={{ fontSize: '1rem', marginBottom: 'var(--space-sm)', color: 'var(--color-text-secondary)' }}>
                  Top Attractions
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-sm)' }}>
                  {destination_info.attractions.slice(0, 8).map((a, i) => (
                    <span key={i} className="interest-tag active" style={{ cursor: 'default' }}>
                      {a.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Weather */}
        {weather_info && (
          <div className="glass-card result-section fade-in stagger-2">
            <h3>
              <span className="section-icon">🌤️</span> Weather
              {weather_info.is_fallback && (
                <span style={{ fontSize: '0.7rem', color: 'var(--color-warning)', marginLeft: 'var(--space-sm)' }}>
                  (Estimated)
                </span>
              )}
            </h3>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)', fontSize: '0.9rem' }}>
              {weather_info.summary}
            </p>
            {weather_info.forecast?.length > 0 && (
              <div className="weather-grid">
                {weather_info.forecast.map((day, i) => (
                  <div key={i} className="weather-day">
                    <div className="weather-date">{formatDate(day.date)}</div>
                    <div className="weather-icon">{WEATHER_ICONS[day.condition] || '🌡️'}</div>
                    <div className="weather-temp">{day.temp_min_c?.toFixed(0)}° – {day.temp_max_c?.toFixed(0)}°</div>
                    <div className="weather-condition">{day.condition}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Budget Breakdown */}
      {budget_breakdown && (
        <div className="glass-card result-section fade-in stagger-3">
          <h3><span className="section-icon">💰</span> Budget Breakdown</h3>
          <div className="budget-items">
            {budget_breakdown.items?.map((item, i) => (
              <div key={i} className="budget-item">
                <div>
                  <div className="budget-item-name">{item.category}</div>
                  {item.notes && (
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                      {item.notes}
                    </div>
                  )}
                </div>
                <div className="budget-item-cost">₹{item.estimated_cost?.toLocaleString('en-IN')}</div>
              </div>
            ))}
          </div>
          <div className="budget-total">
            <div>
              <div>Total Estimated</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 400, color: 'var(--color-text-muted)' }}>
                ₹{budget_breakdown.per_person?.toLocaleString('en-IN')} per person
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
              <span style={{ fontSize: '1.25rem', color: 'var(--color-accent-primary)' }}>
                ₹{budget_breakdown.total_estimated?.toLocaleString('en-IN')}
              </span>
              <span className={`budget-status ${budget_breakdown.is_within_budget ? 'within' : 'over'}`}>
                {budget_breakdown.is_within_budget ? '✓ Within Budget' : '⚠ Over Budget'}
              </span>
            </div>
          </div>
          {budget_breakdown.savings_tips?.length > 0 && (
            <div style={{ marginTop: 'var(--space-lg)' }}>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-sm)' }}>
                💡 Savings Tips
              </h4>
              <ul className="tips-list">
                {budget_breakdown.savings_tips.map((tip, i) => (
                  <li key={i} style={{ '--tip-before': "'💡'" }}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Day-by-Day Itinerary */}
      {itinerary?.days?.length > 0 && (
        <div className="result-section fade-in stagger-4">
          <h3 style={{ fontSize: '1.5rem', marginBottom: 'var(--space-lg)' }}>
            <span className="section-icon">📅</span> Day-by-Day Itinerary
          </h3>
          <div className="itinerary-days">
            {itinerary.days.map((day) => {
              const isOpen = expandedDays[day.day_number] !== false; // default open
              return (
                <div key={day.day_number} className="day-card glass-card" style={{ padding: 0 }}>
                  <div className="day-header" onClick={() => toggleDay(day.day_number)}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <span className="day-number">Day {day.day_number}</span>
                      <span className="day-title">{day.title}</span>
                    </div>
                    <span className={`day-toggle ${isOpen ? 'open' : ''}`}>▼</span>
                  </div>
                  {isOpen && (
                    <div className="day-content">
                      <div className="activity-timeline">
                        {day.activities?.map((activity, i) => (
                          <div key={i} className="activity-item">
                            <div className="activity-time">{activity.time}</div>
                            <div className="activity-title">{activity.title}</div>
                            <div className="activity-desc">{activity.description}</div>
                            <div className="activity-meta">
                              {activity.location && <span>📍 {activity.location}</span>}
                              {activity.duration && <span>⏱️ {activity.duration}</span>}
                              {activity.estimated_cost > 0 && (
                                <span>💰 ₹{activity.estimated_cost.toLocaleString('en-IN')}</span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Food Recommendations */}
      {food_recommendations?.length > 0 && (
        <div className="result-section fade-in stagger-4">
          <h3><span className="section-icon">🍽️</span> Food Recommendations</h3>
          <div className="food-grid">
            {food_recommendations.map((food, i) => (
              <div key={i} className="food-card">
                <div className="food-name">{food.name}</div>
                <span className="food-category">{food.category || food.cuisine}</span>
                {food.is_vegetarian && <span className="veg-badge" style={{ marginLeft: '6px' }}>🌱 Veg</span>}
                <div className="food-desc">{food.description}</div>
                <div className="food-meta">
                  <span>{food.price_range}</span>
                  {food.location_hint && <span>📍 {food.location_hint}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Travel Tips */}
      {travel_tips?.length > 0 && (
        <div className="glass-card result-section fade-in stagger-5">
          <h3><span className="section-icon">💡</span> Travel Tips</h3>
          <ul className="tips-list">
            {travel_tips.map((tip, i) => (
              <li key={i}>{tip}</li>
            ))}
          </ul>
        </div>
      )}

      {/* AI Planning Summary / Review */}
      {review_result && (
        <div className="glass-card result-section fade-in stagger-5">
          <h3><span className="section-icon">🤖</span> AI Planning Summary</h3>
          <div className="review-score">
            <div className={`score-circle ${
              review_result.overall_score >= 7 ? 'high' :
              review_result.overall_score >= 5 ? 'mid' : 'low'
            }`}>
              {review_result.overall_score}/10
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>
                {review_result.approved ? '✅ Plan Approved' : '⚠️ Needs Review'}
              </div>
              <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>
                Quality score based on completeness, budget alignment, and schedule realism
              </div>
            </div>
          </div>
          {review_result.checks?.length > 0 && (
            <div className="review-checks">
              {review_result.checks.map((check, i) => (
                <div key={i} className="review-check">
                  <span className="check-icon">{check.passed ? '✅' : '❌'}</span>
                  <span><strong>{check.check_name}:</strong> {check.details}</span>
                </div>
              ))}
            </div>
          )}
          {review_result.suggestions?.length > 0 && (
            <div style={{ marginTop: 'var(--space-md)' }}>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-sm)' }}>
                Suggestions
              </h4>
              <ul className="tips-list">
                {review_result.suggestions.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
