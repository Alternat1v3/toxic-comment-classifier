import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BsThreeDots } from "react-icons/bs"; 
import './Listing.css'; 

export const Listing = ({ username }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isPopupOpen, setIsPopupOpen] = useState(false); 

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/registered-users/');
        setUsers(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching users:', error);
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const togglePopup = (user) => {
    setSelectedUser(user); 
    setIsPopupOpen(!isPopupOpen); 
  };

  return (
    <div className="container" style={{width:"70%"}}>
      <div className="list_bg">
        <div className="chat_list">
          {loading ? (
            <p>Loading...</p>
          ) : (
            <ul>
              {users.map((user, index) => (
                <div key={index} className="chat_items">
                  <div className="list_details" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div className="profile">
                      <img src={user.pictureUrl} style={{ width: '50px', borderRadius: '100px' }} alt={user.contactName} className="avatar" />
                      <div>
                        <h1 style={{ color: 'whitesmoke', fontWeight: '400' }} className="contact_name">{user.username}</h1>
                        <p className="last_message">{user.email}</p>
                      </div>
                    </div>
                    <div className="col-2">
                      <span className='icon' style={{fontSize:'12px'}} onClick={() => togglePopup(user)}>Show Profile</span> 
                    </div>
                  </div>
                </div>
              ))}
            </ul>
          )}
        </div>
      </div>
      {isPopupOpen && (
        <div className="popup" onClick={() => setIsPopupOpen(false)}>
          <div className='user_pfp' key={selectedUser.id}>
            <img className='pfp' src={selectedUser.profile_photo} />
            <h3>{selectedUser.username}</h3>
            <p>{selectedUser.email}</p>
          </div>
        </div>
      )}
    </div>
  );
};
