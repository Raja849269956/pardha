import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { createSession } from '../api';

function SessionStart() {
  const location = useLocation();
  const profile = location.state?.profile;
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  if (!profile) {
    return (
      <div className="session-start">
        <p>No profile selected. Please select a profile first.</p>
        <button onClick={() => navigate('/profiles')}>Back to Profiles</button>
      </div>
    );
  }

  const handleStart = async () => {
    try {
      const sessionName = name || `${profile.role_title} @ ${profile.target_company || 'Interview'}`;
      const session = await createSession(profile.id, sessionName);
      navigate('/capture', { state: { profile, session } });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start session');
    }
  };

  return (
    <div className="session-start">
      <h2>Start Interview Session</h2>
      <div className="session-profile">
        <strong>{profile.name}</strong>
        <div>{profile.role_title} @ {profile.target_company || 'Unknown'}</div>
        <div className="session-meta">{profile.tone} · {profile.answer_length}</div>
      </div>
      <input
        placeholder="Session name (optional)"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      {error && <div className="error">{error}</div>}
      <div className="session-actions">
        <button onClick={handleStart}>Start Capturing</button>
        <button onClick={() => navigate('/profiles')}>Back</button>
      </div>
    </div>
  );
}

export default SessionStart;
