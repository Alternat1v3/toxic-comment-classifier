import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { HiOutlineMagnifyingGlass, HiPaperAirplane, HiOutlineShieldCheck } from 'react-icons/hi2';
import { chat, moderation } from '../api';
import Avatar from '../components/Avatar';
import ToxicityBadge from '../components/ToxicityBadge';
import useChatSocket from '../hooks/useChatSocket';

const MAX_LENGTH = 1000;
const time = (iso) => new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

export default function ChatPage({ user }) {
  const { username } = useParams();
  const [contacts, setContacts] = useState(null);
  const [query, setQuery] = useState('');
  const [classifier, setClassifier] = useState(null);

  useEffect(() => {
    chat.contacts().then(setContacts).catch(() => setContacts([]));
    moderation.status().then((s) => setClassifier(s.source)).catch(() => {});
  }, []);

  const visible = useMemo(
    () => (contacts || []).filter((c) => c.username.toLowerCase().includes(query.trim().toLowerCase())),
    [contacts, query]
  );
  const contact = contacts?.find((c) => c.username === username);

  return (
    <div className={`chat${username ? ' chat--open' : ''}`}>
      <aside className="contacts">
        <header className="contacts__header">
          <h1>Chats</h1>
          <label className="search">
            <HiOutlineMagnifyingGlass aria-hidden="true" />
            <input placeholder="Search people" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search people" />
          </label>
        </header>
        {contacts === null ? (
          <p className="muted contacts__empty">Loading…</p>
        ) : visible.length === 0 ? (
          <p className="muted contacts__empty">{contacts.length ? 'Nobody matches that search.' : 'No one else has signed up yet.'}</p>
        ) : (
          <ul className="contacts__list">
            {visible.map((c) => (
              <li key={c.id}>
                <Link to={`/chat/${encodeURIComponent(c.username)}`} className={`contact${c.username === username ? ' is-active' : ''}`}>
                  <Avatar user={c} size={40} />
                  <span className="contact__name">{c.username}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </aside>

      {username ? (
        <Conversation key={username} me={user} username={username} contact={contact} classifier={classifier} />
      ) : (
        <section className="conversation conversation--empty">
          <HiOutlineShieldCheck className="empty-icon" aria-hidden="true" />
          <h2>Pick someone to chat with</h2>
          <p className="muted">Messages are checked as you send them. Flagged ones show a label, and offensive words are replaced for the other person.</p>
        </section>
      )}
    </div>
  );
}

function Conversation({ me, username, contact, classifier }) {
  const { messages, status, error, send } = useChatSocket(username);
  const [draft, setDraft] = useState('');
  const listRef = useRef(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages]);

  const submit = (event) => {
    event.preventDefault();
    const text = draft.trim();
    if (text && send(text)) setDraft('');
  };

  return (
    <section className="conversation">
      <header className="conversation__header">
        <Link to="/" className="back-link" aria-label="Back to chats">
          ‹
        </Link>
        <Avatar user={contact || { username }} size={40} />
        <div>
          <h2>{username}</h2>
          <span className={`status status--${status}`}>{status === 'open' ? 'Connected' : status === 'reconnecting' ? 'Reconnecting…' : status === 'closed' ? 'Disconnected' : 'Connecting…'}</span>
        </div>
        {classifier && (
          <span className="chip" title="What checks each message">
            {classifier === 'bert' ? 'Checked by BERT' : 'Checked by keyword list'}
          </span>
        )}
      </header>

      <ol className="messages" ref={listRef} aria-live="polite">
        {messages.length === 0 && status === 'open' && <li className="muted messages__empty">No messages yet. Say hello!</li>}
        {messages.map((m) => {
          const mine = m.sender === me.username;
          return (
            <li key={m.id} className={`message${mine ? ' message--mine' : ''}`}>
              <div className={`bubble${m.toxicity_label !== 'non-toxic' ? ' bubble--flagged' : ''}`}>{m.message}</div>
              <div className="message__meta">
                <ToxicityBadge label={m.toxicity_label} score={m.toxicity_score} />
                <time dateTime={m.timestamp}>{time(m.timestamp)}</time>
              </div>
            </li>
          );
        })}
      </ol>

      {error && (
        <p className="alert conversation__error" role="alert">
          {error}
        </p>
      )}

      <form className="composer" onSubmit={submit}>
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={`Message ${username}`}
          maxLength={MAX_LENGTH}
          aria-label={`Message ${username}`}
          disabled={status !== 'open'}
        />
        <button className="button button--primary composer__send" type="submit" disabled={status !== 'open' || !draft.trim()} aria-label="Send">
          <HiPaperAirplane aria-hidden="true" />
        </button>
      </form>
    </section>
  );
}
