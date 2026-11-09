import React, { useCallback, useEffect, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { auth } from './api';
import Layout from './components/Layout';
import RulesModal from './components/RulesModal';
import AuthPage from './pages/AuthPage';
import ChatPage from './pages/ChatPage';
import FeedbackPage from './pages/FeedbackPage';
import ModerationLab from './pages/ModerationLab';
import SettingsPage from './pages/SettingsPage';
import { useTheme } from './theme';

export default function App() {
  // undefined = still asking the server, null = signed out
  const [user, setUser] = useState(undefined);
  const [theme, setTheme] = useTheme();

  useEffect(() => {
    auth.csrf().catch(() => {});
    auth.me().then(setUser).catch(() => setUser(null));
  }, []);

  const signOut = useCallback(async () => {
    await auth.logout().catch(() => {});
    setUser(null);
  }, []);

  if (user === undefined) {
    return <div className="splash" aria-busy="true">Loading…</div>;
  }

  return (
    <BrowserRouter>
      {user ? (
        <>
          <Layout user={user} onSignOut={signOut}>
            <Routes>
              <Route path="/" element={<ChatPage user={user} />} />
              <Route path="/chat/:username" element={<ChatPage user={user} />} />
              <Route path="/moderation" element={<ModerationLab />} />
              <Route path="/feedback" element={<FeedbackPage />} />
              <Route path="/settings" element={<SettingsPage theme={theme} onThemeChange={setTheme} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Layout>
          <RulesModal />
        </>
      ) : (
        <Routes>
          <Route path="/register" element={<AuthPage mode="register" onSignedIn={setUser} />} />
          <Route path="*" element={<AuthPage mode="login" onSignedIn={setUser} />} />
        </Routes>
      )}
    </BrowserRouter>
  );
}
