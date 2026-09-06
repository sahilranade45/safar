import { useState, useEffect } from 'react';

const AGENTS = [
  { key: 'Coordinator', name: 'Coordinator Agent', icon: '🎯', desc: 'Validating request & orchestrating team' },
  { key: 'Destination Research', name: 'Destination Research Agent', icon: '🔍', desc: 'Researching destination & attractions' },
  { key: 'Budget Analyst', name: 'Budget Analyst Agent', icon: '💰', desc: 'Analyzing costs & budget breakdown' },
  { key: 'Itinerary Planner', name: 'Itinerary Planner Agent', icon: '📅', desc: 'Creating day-by-day itinerary' },
  { key: 'Review Agent', name: 'Review Agent', icon: '✅', desc: 'Reviewing plan for quality & consistency' },
  { key: 'Coordinator (Finalize)', name: 'Coordinator (Finalize)', icon: '🎯', desc: 'Assembling final travel plan' },
];

export default function AgentProgress({ agentExecutions, isLoading }) {
  const [simulatedIndex, setSimulatedIndex] = useState(0);

  // Simulate progress while loading (no real-time streaming in MVP)
  useEffect(() => {
    if (!isLoading) {
      setSimulatedIndex(0);
      return;
    }

    setSimulatedIndex(0);
    const delays = [500, 3000, 6000, 9000, 12000, 14000];

    const timers = delays.map((delay, i) =>
      setTimeout(() => setSimulatedIndex(i + 1), delay)
    );

    return () => timers.forEach(clearTimeout);
  }, [isLoading]);

  const getAgentStatus = (agent, index) => {
    // If we have real execution data, use it
    if (agentExecutions && agentExecutions.length > 0) {
      const exec = agentExecutions.find(e => e.agent_name === agent.key);
      if (exec) return exec.status;
      return 'pending';
    }

    // Otherwise simulate based on timer
    if (!isLoading) return 'pending';
    if (index < simulatedIndex) return 'completed';
    if (index === simulatedIndex) return 'running';
    return 'pending';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✓';
      case 'running': return '⟳';
      case 'failed': return '✗';
      default: return '○';
    }
  };

  const getDuration = (agent) => {
    if (!agentExecutions) return null;
    const exec = agentExecutions.find(e => e.agent_name === agent.key);
    return exec?.duration_seconds ? `${exec.duration_seconds.toFixed(1)}s` : null;
  };

  return (
    <div className="agent-progress fade-in">
      <h2 className="agent-progress-title">
        {isLoading ? '✨ Planning your trip...' : '🤖 AI Team Execution'}
      </h2>
      <div className="agent-list">
        {AGENTS.map((agent, index) => {
          const status = getAgentStatus(agent, index);
          const duration = getDuration(agent);

          return (
            <div key={agent.key}>
              <div className={`agent-item ${status}`}>
                <div className={`agent-icon ${status}`}>
                  {status === 'completed' ? getStatusIcon(status) :
                   status === 'running' ? getStatusIcon(status) :
                   status === 'failed' ? getStatusIcon(status) :
                   agent.icon}
                </div>
                <div className="agent-info">
                  <div className="agent-name">{agent.name}</div>
                  <div className="agent-status-text">
                    {status === 'running' ? agent.desc :
                     status === 'completed' ? `Done${duration ? ` in ${duration}` : ''}` :
                     status === 'failed' ? 'Failed' :
                     'Waiting...'}
                  </div>
                </div>
              </div>
              {index < AGENTS.length - 1 && (
                <div className={`agent-connector ${status === 'completed' ? 'completed' : ''}`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
