import React, { useState } from 'react';
import { mediaUrl } from '../api';

const HUES = [222, 262, 330, 12, 32, 152, 190];

/** Profile photo, or the user's initial on a colour picked from their name. */
export default function Avatar({ user, size = 40 }) {
  const [broken, setBroken] = useState(false);
  const src = mediaUrl(user?.profile_photo);
  const name = user?.username || '?';
  const style = { width: size, height: size, fontSize: size * 0.42 };

  if (src && !broken) {
    return <img className="avatar" src={src} alt="" style={style} onError={() => setBroken(true)} />;
  }
  const hue = HUES[[...name].reduce((sum, ch) => sum + ch.charCodeAt(0), 0) % HUES.length];
  return (
    <span className="avatar avatar--initial" style={{ ...style, '--hue': hue }} aria-hidden="true">
      {name[0].toUpperCase()}
    </span>
  );
}
