import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { auth, errorMessage } from '../api';

export default function AuthPage({ mode, onSignedIn }) {
  const isRegister = mode === 'register';
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [photo, setPhoto] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      let user;
      if (isRegister) {
        const data = new FormData();
        Object.entries(form).forEach(([key, value]) => data.append(key, value));
        if (photo) data.append('profile_photo', photo);
        user = await auth.register(data);
      } else {
        user = await auth.login(form.username, form.password);
      }
      onSignedIn(user);
      navigate('/');
    } catch (err) {
      setError(errorMessage(err, isRegister ? 'Could not create the account.' : 'Could not sign in.'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth">
      <section className="auth__intro">
        <span className="logo-mark logo-mark--large" aria-hidden="true">S</span>
        <h1>SafeChat</h1>
        <p>Real-time chat where every message is checked by a fine-tuned BERT model. Insults, threats and slurs are flagged and softened before anyone sees them.</p>
        <ul className="auth__points">
          <li>Seven labels, from insult to identity hate</li>
          <li>Offensive words replaced as you chat</li>
          <li>A moderation lab to try the model yourself</li>
        </ul>
      </section>

      <form className="card auth__form" onSubmit={submit} noValidate>
        <h2>{isRegister ? 'Create an account' : 'Sign in'}</h2>
        {error && (
          <p className="alert" role="alert">
            {error}
          </p>
        )}
        <label>
          Username
          <input name="username" value={form.username} onChange={update} autoComplete="username" required autoFocus />
        </label>
        {isRegister && (
          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={update} autoComplete="email" required />
          </label>
        )}
        <label>
          Password
          <input
            name="password"
            type="password"
            value={form.password}
            onChange={update}
            autoComplete={isRegister ? 'new-password' : 'current-password'}
            required
          />
        </label>
        {isRegister && (
          <label>
            Profile photo <span className="muted">(optional)</span>
            <input type="file" accept="image/*" onChange={(event) => setPhoto(event.target.files[0] || null)} />
          </label>
        )}
        <button className="button button--primary" type="submit" disabled={busy}>
          {busy ? 'Please wait…' : isRegister ? 'Create account' : 'Sign in'}
        </button>
        <p className="muted auth__switch">
          {isRegister ? 'Already have an account? ' : 'New here? '}
          <Link to={isRegister ? '/' : '/register'}>{isRegister ? 'Sign in' : 'Create an account'}</Link>
        </p>
      </form>
    </div>
  );
}
