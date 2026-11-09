import React, { useState, useEffect } from 'react';
import './Verification.css';

export const Verification = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Retrieve dark mode state from localStorage when the component mounts
    const savedMode = localStorage.getItem('darkMode') === 'true';
    setIsDarkMode(savedMode);

    // Apply dark mode class to the body on component mount
    if (savedMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, []);

  const handleToggle = () => {
    setIsDarkMode(prevMode => {
      const newMode = !prevMode;
      localStorage.setItem('darkMode', newMode);

      // Apply or remove dark mode class on body element
      if (newMode) {
        document.body.classList.add('dark-mode');
      } else {
        document.body.classList.remove('dark-mode');
      }

      return newMode;
    });
  };

  return (
    <div className="verification-container">
      <div className="rules-box">
        <h2>Rules</h2>
        <ul>
          <li>Be respectful to others.</li>
          <li>Follow the community guidelines.</li>
          <li>Report any inappropriate behavior.</li>
          <li>Do not share personal information.</li>
          <li>Keep conversations relevant and on-topic.</li>
          <li>No spamming or excessive messaging.</li>
          <li>Do not use offensive language or hate speech.</li>
          <li>Respect others' privacy and personal boundaries.</li>
          <li>Do not engage in or promote illegal activities.</li>
          <li>Use appropriate usernames and profile pictures.</li>
        </ul>
      </div>
      <div className="dark-mode-box">
        <h2>Dark Mode</h2>
        <label className="switch">
          <input
            type="checkbox"
            checked={isDarkMode}
            onChange={handleToggle}
          />
          <span className="slider round"></span>
        </label>
      </div>
    </div>
  );
};
