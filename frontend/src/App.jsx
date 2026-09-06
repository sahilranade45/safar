import { useState, useEffect } from 'react';
import TripForm from './components/TripForm';
import AgentProgress from './components/AgentProgress';
import TravelPlan from './components/TravelPlan';
import ReplanPanel from './components/ReplanPanel';
import { checkHealth, createPlan, replanTrip } from './api/client';

export default function App() {
  const [view, setView] = useState('form'); // form | loading | results
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [backendOk, setBackendOk] = useState(null);
  const [apiKeyConfigured, setApiKeyConfigured] = useState(false);

  // Travel plan state
  const [planResponse, setPlanResponse] = useState(null);
  const [originalRequest, setOriginalRequest] = useState(null);

  // Check backend health on mount
  useEffect(() => {
    checkHealth()
      .then(data => {
        setBackendOk(true);
        setApiKeyConfigured(data.api_key_configured);
      })
      .catch(() => setBackendOk(false));
  }, []);

  const handlePlanSubmit = async (request) => {
    setError('');
    setIsLoading(true);
    setView('loading');
    setOriginalRequest(request);
    setPlanResponse(null);

    try {
      const response = await createPlan(request);

      if (response.success && response.plan) {
        setPlanResponse(response);
        setView('results');
      } else {
        setError(response.error || 'Failed to generate travel plan.');
        setView('form');
      }
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
      setView('form');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReplan = async (replanRequest) => {
    setError('');
    setIsLoading(true);
    setView('loading');
    setPlanResponse(null);

    try {
      const response = await replanTrip(replanRequest);

      if (response.success && response.plan) {
        setPlanResponse(response);
        setView('results');
      } else {
        setError(response.error || 'Replanning failed.');
        setView('results'); // Go back to old results on replan failure
      }
    } catch (err) {
      setError(err.message || 'Replanning failed. Please try again.');
      setView('results');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewTrip = () => {
    setView('form');
    setPlanResponse(null);
    setOriginalRequest(null);
    setError('');
  };

  return (
    <div>
      {/* Navbar */}
      <nav className="navbar">
        <div className="container">
          <div className="logo" onClick={handleNewTrip} style={{ cursor: 'pointer' }}>
            <svg className="logo-icon" viewBox="0 0 100 100">
              <defs>
                <linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#6366f1' }} />
                  <stop offset="100%" style={{ stopColor: '#ec4899' }} />
                </linearGradient>
              </defs>
              <circle cx="50" cy="50" r="48" fill="url(#lg)" />
              <text x="50" y="66" fontFamily="Arial" fontSize="45" fontWeight="bold" textAnchor="middle" fill="white">S</text>
            </svg>
            <div>
              <div className="logo-text">Safar</div>
            </div>
          </div>
          <div className="tagline">Your trip, planned by a team of AI agents.</div>
        </div>
      </nav>

      <main className="container">
        {/* Backend Status Banner */}
        {backendOk === false && (
          <div className="error-banner" style={{ marginTop: 'var(--space-lg)' }}>
            ⚠️ Cannot connect to the backend server. Make sure it's running on port 8000.
            <br />
            <code style={{ fontSize: '0.85rem' }}>cd backend && uvicorn app.main:app --reload</code>
          </div>
        )}

        {backendOk === true && !apiKeyConfigured && (
          <div className="error-banner" style={{
            marginTop: 'var(--space-lg)',
            background: 'rgba(245, 158, 11, 0.1)',
            borderColor: 'rgba(245, 158, 11, 0.3)',
            color: 'var(--color-warning)'
          }}>
            ⚠️ Gemini API key not configured. Set <code>GEMINI_API_KEY</code> in your <code>.env</code> file.
          </div>
        )}

        {/* Error Banner */}
        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        {/* Form View */}
        {view === 'form' && (
          <>
            <section className="hero">
              <h1>Plan Your Perfect Trip</h1>
              <p>
                Our team of 5 AI agents will research, budget, plan, and review
                your personalized travel itinerary in seconds.
              </p>
            </section>
            <TripForm onSubmit={handlePlanSubmit} isLoading={isLoading} />
          </>
        )}

        {/* Loading View */}
        {view === 'loading' && (
          <AgentProgress
            agentExecutions={planResponse?.agent_executions}
            isLoading={isLoading}
          />
        )}

        {/* Results View */}
        {view === 'results' && planResponse?.plan && (
          <>
            {/* Back to form button */}
            <div style={{ textAlign: 'center', marginTop: 'var(--space-xl)' }}>
              <button className="btn btn-secondary" onClick={handleNewTrip}>
                ← Plan Another Trip
              </button>
            </div>

            {/* Agent Execution Summary */}
            <AgentProgress
              agentExecutions={planResponse.agent_executions}
              isLoading={false}
            />

            {/* Travel Plan */}
            <TravelPlan
              plan={planResponse.plan}
              totalDuration={planResponse.total_duration_seconds}
            />

            {/* Replan Panel */}
            <ReplanPanel
              originalRequest={originalRequest}
              existingPlan={planResponse.plan}
              onReplan={handleReplan}
              isLoading={isLoading}
            />
          </>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        textAlign: 'center',
        padding: 'var(--space-2xl) 0',
        borderTop: '1px solid var(--border-color)',
        marginTop: 'var(--space-3xl)',
        color: 'var(--color-text-muted)',
        fontSize: '0.85rem',
      }}>
        <p>
          <strong style={{ color: 'var(--color-text-secondary)' }}>Safar</strong> — Multi-Agent AI Travel Planner
        </p>
        <p style={{ marginTop: 'var(--space-xs)' }}>
          Built with LangGraph · Google Gemini · FastAPI · React
        </p>
      </footer>
    </div>
  );
}
