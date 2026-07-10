import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import Login from './components/Login';
import ProfileManager from './components/ProfileManager';
import SessionStart from './components/SessionStart';
import AudioCapture from './components/AudioCapture';
import Overlay from './components/Overlay';
import { initApiUrl, getMe } from './api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const isOverlay = location.pathname === '/overlay';

  useEffect(() => {
    initApiUrl().then(() => {
      const token = localStorage.getItem('token');
      if (token) {
        getMe()
          .then((data) => setUser(data))
          .catch(() => {
            localStorage.removeItem('token');
          })
          .finally(() => setLoading(false));
      } else {
        setLoading(false);
      }
    });
  }, []);

  useEffect(() => {
    if (!loading && !user && !isOverlay) {
      navigate('/login');
    } else if (!loading && user && location.pathname === '/') {
      navigate('/profiles');
    }
  }, [loading, user, isOverlay, location.pathname, navigate]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className={isOverlay ? 'overlay-app' : 'app'}>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login onLogin={setUser} />} />
        <Route path="/profiles" element={<ProfileManager user={user} />} />
        <Route path="/session" element={<SessionStart />} />
        <Route path="/capture" element={<AudioCapture />} />
        <Route path="/overlay" element={<Overlay />} />
      </Routes>
    </div>
  );
}

export default App;
