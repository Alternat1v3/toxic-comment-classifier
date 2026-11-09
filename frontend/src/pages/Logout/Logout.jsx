import React from 'react';
import axios from 'axios';
import { CiLogout } from "react-icons/ci";
import Cookies from 'js-cookie'; // Import js-cookie to access cookies easily
import '../Logout/Logout.css';

export const Logout = () => {
  const handleLogout = async () => {
    try {
     
      Cookies.remove('csrftoken'); 
      Cookies.remove('sessionid');
     
      const response = await axios.post('http://127.0.0.1:8000/logout/', {}, {
        withCredentials: true,  
      });

      console.log('Logout successful', response);

      localStorage.removeItem('loggedIn');
      localStorage.removeItem('username');
      
      window.location.href = '/login'; 

    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div className='logout'>
      <CiLogout className='icon-log' />
      <h2>Are you sure?</h2>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
};

export default Logout;


