// Built by "Zohaib Iqbal" CS619
// Contact: Zohaibiqbal639@gmail.com, bc200204155@vu.edu.pk
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import Sidebar from './component/Sidebar.jsx';
import { Contacts } from './pages/Contacts/Contacts.jsx';
import { Listing } from './pages/Listing/Listing.jsx';
import { Search } from './pages/Search/Search.jsx';
import { Matches } from './pages/Matches/Matches.jsx';
import { Feedback } from './pages/Feedback/Feedback.jsx';
import { Profile } from './pages/Profile/Profile.jsx';
import { Verification } from './pages/Verification/Verification.jsx';
import { Logout } from './pages/Logout/Logout.jsx';
import { Interface } from './pages/Interface/Interface.jsx';
import RegisteredUsers from './pages/Register/Register.jsx';
import Login from './pages/Login/Login.jsx';
import axios from 'axios';
import Modal from './pages/Modal/modal.jsx'; 
import Cookies from 'js-cookie'; 

function App() {
  const [showRegister, setShowRegister] = useState(true);
  const [showLogin, setShowLogin] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [registeredUsers, setRegisteredUsers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false); 
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [redirected, setRedirected] = useState(false); 

  useEffect(() => {
   
    const csrfToken = Cookies.get('csrftoken');
    if (!csrfToken && !redirected) { 
      handleLogout(); 
      setRedirected(true); 
    }

  
    const savedMode = localStorage.getItem('darkMode') === 'true';
    setIsDarkMode(savedMode);

    if (savedMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }

    const userLoggedIn = localStorage.getItem('loggedIn') === 'true';
    setLoggedIn(userLoggedIn);
    setShowRegister(!userLoggedIn);
    const storedUsername = localStorage.getItem('username');
    const showModal = localStorage.getItem('showModal') !== 'false';

    if (userLoggedIn && storedUsername) {
      setUsername(storedUsername);
      if (showModal) {
        setIsModalOpen(true); 
      }
    }
  }, [redirected]); 

  useEffect(() => {
    const fetchRegisteredUsers = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/registered-users/');
        setRegisteredUsers(response.data.filter(user => user.username !== username));
      } catch (error) {
        console.error('Error fetching registered users:', error);
      }
    };

    fetchRegisteredUsers();
  }, [username]);

  const handleRegisterComplete = () => {
    setShowRegister(false);
    setShowLogin(true);
  };

  const handleLoginComplete = (username) => {
    setShowLogin(false);
    setLoggedIn(true);
    setUsername(username);
    localStorage.setItem('loggedIn', 'true');
    localStorage.setItem('username', username);
    const showModal = localStorage.getItem('showModal') !== 'false';
    if (showModal) {
      setIsModalOpen(true); 
    }
  };

  const handleLogout = () => {
   
    setLoggedIn(false);
    localStorage.removeItem('loggedIn');
    localStorage.removeItem('username');
    setShowRegister(true);
    setShowLogin(false);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleCheckboxChange = (isChecked) => {
    localStorage.setItem('showModal', isChecked ? 'false' : 'true');
  };

  const handleDarkModeToggle = () => {
    setIsDarkMode(prevMode => {
      const newMode = !prevMode;
      localStorage.setItem('darkMode', newMode);

      if (newMode) {
        document.body.classList.add('dark-mode');
      } else {
        document.body.classList.remove('dark-mode');
      }

      return newMode;
    });
  };

  return (
    <BrowserRouter>
      <div>
        {loggedIn ? (
          <>
            <Sidebar>
              <div className="container">
                <Contacts username={username} />
                <Routes>
                  <Route path="/" element={<></>} />
                  <Route path="/Contact" element={<Contacts />} />
                  <Route path="/Listing" element={<Listing />} />
                  <Route path="/Search" element={<Search />} />
                  <Route path="/Matches" element={<Matches />} />
                  <Route path="/Feedback" element={<Feedback />} />
                  <Route path="/Profile" element={<Profile />} />
                  <Route path="/Settings" element={<Verification />} />
                  <Route path="/Interface/:id" element={<Interface contacts={registeredUsers} username={username} isDarkMode={isDarkMode} />} />
                  <Route path="/logout" element={<Logout onLogout={handleLogout} />} />
                  <Route path="*" element={<Navigate to="/" />} />
                </Routes>
              </div>
            </Sidebar>
            <Modal isOpen={isModalOpen} onClose={handleCloseModal} onCheckboxChange={handleCheckboxChange} />
          </>
        ) : (
          <div>
            {showRegister && <RegisteredUsers onRegister={handleRegisterComplete} />}
            {showLogin && <Login onLogin={handleLoginComplete} />}
          </div>
        )}
      </div>
    </BrowserRouter>
  );
}

export default App;


