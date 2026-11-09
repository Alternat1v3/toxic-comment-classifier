import React from 'react';
import { HiOutlineExclamationTriangle } from 'react-icons/hi2';

const SEVERE = new Set(['threat', 'identity hate', 'severe toxic']);

/** Shown under a message the classifier flagged. */
export default function ToxicityBadge({ label, score }) {
  if (!label || label === 'non-toxic') return null;
  const percent = typeof score === 'number' ? ` · ${Math.round(score * 100)}%` : '';
  return (
    <span className={`badge ${SEVERE.has(label) ? 'badge--severe' : 'badge--warn'}`} title="Flagged by the toxicity classifier">
      <HiOutlineExclamationTriangle aria-hidden="true" />
      {label}
      {percent}
    </span>
  );
}
