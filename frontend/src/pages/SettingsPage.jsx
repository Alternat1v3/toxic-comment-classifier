import React from 'react';
import { RULES } from '../components/RulesModal';

export default function SettingsPage({ theme, onThemeChange }) {
  return (
    <div className="page">
      <header className="page__header">
        <h1>Settings</h1>
      </header>

      <section className="card setting">
        <div>
          <h2>Dark mode</h2>
          <p className="muted">Easier on the eyes at night.</p>
        </div>
        <label className="switch">
          <input type="checkbox" checked={theme === 'dark'} onChange={(e) => onThemeChange(e.target.checked ? 'dark' : 'light')} />
          <span className="switch__track" aria-hidden="true" />
          <span className="sr-only">Dark mode</span>
        </label>
      </section>

      <section className="card">
        <h2>Community rules</h2>
        <ul className="rules">
          {RULES.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
        <p className="muted">Messages that break these rules are flagged by the classifier and visible to moderators in the admin panel.</p>
      </section>
    </div>
  );
}
