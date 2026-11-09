import React, { useState } from 'react';
import { errorMessage, moderation } from '../api';
import ToxicityBadge from '../components/ToxicityBadge';

const EXAMPLES = [
  'Thanks for the notes, see you tomorrow!',
  'You are a complete idiot.',
  'I will find you and hurt you.',
  'Shut the fuck up.',
];

export default function ModerationLab() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const check = async (value) => {
    const input = (value ?? text).trim();
    if (!input) return;
    setText(input);
    setBusy(true);
    setError('');
    try {
      setResult({ text: input, ...(await moderation.check(input)) });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const scores = result?.scores ? Object.entries(result.scores).sort((a, b) => b[1] - a[1]) : [];

  return (
    <div className="page">
      <header className="page__header">
        <h1>Moderation lab</h1>
        <p className="muted">Try the classifier on any text. Nothing is sent to anyone.</p>
      </header>

      <form
        className="card lab__form"
        onSubmit={(e) => {
          e.preventDefault();
          check();
        }}
      >
        <label htmlFor="lab-text">Message</label>
        <textarea id="lab-text" rows={3} maxLength={1000} value={text} onChange={(e) => setText(e.target.value)} placeholder="Type something to check…" />
        <div className="lab__actions">
          <div className="lab__examples">
            {EXAMPLES.map((example) => (
              <button type="button" key={example} className="button button--ghost button--small" onClick={() => check(example)}>
                {example}
              </button>
            ))}
          </div>
          <button className="button button--primary" type="submit" disabled={busy || !text.trim()}>
            {busy ? 'Checking…' : 'Check'}
          </button>
        </div>
      </form>

      {error && (
        <p className="alert" role="alert">
          {error}
        </p>
      )}

      {result && (
        <section className="card lab__result" aria-live="polite">
          <div className="lab__verdict">
            {result.is_toxic ? <ToxicityBadge label={result.label} score={result.score} /> : <span className="badge badge--ok">non-toxic · {Math.round(result.score * 100)}%</span>}
            <span className="muted">via {result.source === 'bert' ? 'the BERT model' : 'the keyword list (model not loaded)'}</span>
          </div>
          <dl className="lab__shown">
            <dt>What the other person would see</dt>
            <dd>{result.shown_as}</dd>
          </dl>
          {scores.length > 0 && (
            <ul className="scores" aria-label="Probability of each label">
              {scores.map(([label, p]) => (
                <li key={label} className={label === result.label ? 'is-top' : ''}>
                  <span className="scores__label">{label}</span>
                  <span className="scores__bar" aria-hidden="true">
                    <span style={{ width: `${Math.max(p * 100, 0.5)}%` }} />
                  </span>
                  <span className="scores__value">{(p * 100).toFixed(1)}%</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}
