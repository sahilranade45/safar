/**
 * Safar — API Client
 *
 * Handles all communication with the FastAPI backend.
 */

const API_BASE = '/api';

/**
 * Check backend health status.
 * @returns {Promise<Object>} Health response
 */
export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Backend not available');
  return res.json();
}

/**
 * Create a new travel plan.
 * @param {Object} request - Travel plan request
 * @returns {Promise<Object>} Travel plan response with agent executions
 */
export async function createPlan(request) {
  const res = await fetch(`${API_BASE}/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || err.error || `Request failed (${res.status})`);
  }

  return res.json();
}

/**
 * Replan an existing travel plan with modifications.
 * @param {Object} replanRequest - Contains original_request, modification, existing_plan
 * @returns {Promise<Object>} Updated travel plan response
 */
export async function replanTrip(replanRequest) {
  const res = await fetch(`${API_BASE}/replan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(replanRequest),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || err.error || `Replan failed (${res.status})`);
  }

  return res.json();
}
