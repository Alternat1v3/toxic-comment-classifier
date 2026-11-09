import React, { useState } from 'react';
import { errorMessage, feedback } from '../api';

export default function FeedbackPage() {
  const [text, setText] = useState('');
  const [state, setState] = useState({ busy: false, sent: false, error: '' });

  const submit = async (event) => {
    event.preventDefault();
    setState({ busy: true, sent: false, error: '' });
    try {
      await feedback.send(text.trim());
      setText('');
      setState({ busy: false, sent: true, error: '' });
    } catch (err) {
      setState({ busy: false, sent: false, error: errorMessage(err) });
    }
  };

  return (
    <div className="page">
      <header className="page__header">
        <h1>Feedback</h1>
        <p className="muted">Tell us what works and what doesn't. Feedback is anonymous: your name is not stored with it.</p>
      </header>
      <form className="card" onSubmit={submit}>
        <label htmlFor="feedback">Your feedback</label>
        <textarea id="feedback" rows={5} maxLength={2000} value={text} onChange={(e) => setText(e.target.value)} required />
        {state.error && (
          <p className="alert" role="alert">
            {state.error}
          </p>
        )}
        {state.sent && <p className="success">Thank you, your feedback was sent.</p>}
        <button className="button button--primary" type="submit" disabled={state.busy || !text.trim()}>
          {state.busy ? 'Sending…' : 'Send feedback'}
        </button>
      </form>
    </div>
  );
}
