import React, { useState } from 'react';
import './Feedback.css';
import axios from 'axios';
import Cookies from 'js-cookie';

export const Feedback = () => {
  const [feedback, setFeedback] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');  

  const handleSubmit = async (e) => {
    e.preventDefault();
    const csrfToken = Cookies.get('csrftoken'); 

    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/api/feedback/',
        { feedback },
        {
          headers: {
            'X-CSRFToken': csrfToken,
          },
          withCredentials: true, 
        }
      );
      console.log('Feedback submitted successfully:', response.data);
      setFeedback('');  
      setSuccessMessage('Thank you for your feedback!'); 
      setError(''); 
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setError('There was an issue submitting your feedback. Try again later or Log in again');
      setSuccessMessage('');  
    }
  };

  return (
    <div>
      <h2>Submit Feedback (it will be Anonymous)</h2>
      <form onSubmit={handleSubmit}>
        <textarea 
          value={feedback} 
          onChange={(e) => setFeedback(e.target.value)} 
          required 
        />
        <button type="submit">Submit</button>
      </form>
      {error && <p className="error">{error}</p>}
      {successMessage && <p className="success">{successMessage}</p>}  
    </div>
  );
};

export default Feedback;
 