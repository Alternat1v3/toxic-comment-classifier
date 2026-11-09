import React, { useEffect, useRef, useState } from 'react';

const KEY = 'rulesAccepted';
export const RULES = [
  'Be respectful to others.',
  'No insults, threats, slurs or hate speech.',
  'Do not share personal information.',
  'No spam or excessive messaging.',
];

function alreadyAccepted() {
  try {
    return localStorage.getItem(KEY) === 'yes';
  } catch {
    return false;
  }
}

/** Community rules, shown once after signing in. */
export default function RulesModal() {
  const [open, setOpen] = useState(() => !alreadyAccepted());
  const button = useRef(null);

  useEffect(() => {
    if (open) button.current?.focus();
  }, [open]);

  if (!open) return null;

  const accept = () => {
    try {
      localStorage.setItem(KEY, 'yes');
    } catch {
      // not fatal: the rules will just show again next time
    }
    setOpen(false);
  };

  return (
    <div className="modal-backdrop">
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="rules-title">
        <h2 id="rules-title">Before you chat</h2>
        <p className="muted">Every message is checked by a toxicity classifier. Offensive words are replaced, and flagged messages are visible to moderators.</p>
        <ul className="rules">
          {RULES.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
        <button ref={button} className="button button--primary" onClick={accept}>
          Got it
        </button>
      </div>
    </div>
  );
}
