import { useEffect, useState } from 'react';

const KEY = 'theme';

function initialTheme() {
  try {
    const saved = localStorage.getItem(KEY);
    if (saved === 'light' || saved === 'dark') return saved;
  } catch {
    // storage can be unavailable (private windows); fall back to the system setting
  }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/** Light or dark theme, remembered between visits. */
export function useTheme() {
  const [theme, setTheme] = useState(initialTheme);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem(KEY, theme);
    } catch {
      // not fatal: the theme just won't be remembered
    }
  }, [theme]);
  return [theme, setTheme];
}
