// src/components/Modal.js
import React, { useState } from 'react';
import './modal.css'; // Import CSS for styling

const Modal = ({ isOpen, onClose, onCheckboxChange }) => {
  const [checked, setChecked] = useState(false);

  if (!isOpen) return null;

  const handleCheckboxChange = (e) => {
    setChecked(e.target.checked);
    onCheckboxChange(e.target.checked);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="close-button" onClick={onClose}>×</button>
        <h2>Rules</h2>
        <ul>
          <li>Be respectful to others.</li>
          <li>Follow the community guidelines.</li>
          <li>Report any inappropriate behavior.</li>
        </ul>
        <div className="checkbox-container">
          <input
            type="checkbox"
            id="dont-show-again"
            checked={checked}
            onChange={handleCheckboxChange}
          />
          <label htmlFor="dont-show-again">Don't show this again</label>
        </div>
      </div>
    </div>
  );
};

export default Modal;
