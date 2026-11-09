//  Built by "Zohaib Iqbal" CS619
//  Contact: Zohaibiqbal639@gmail.com, bc200204155@vu.edu.pk

import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import '../Contacts/Contacts.css';
import axios from 'axios'; 

export const Contacts = ({ username }) => {
    const [registeredUsers, setRegisteredUsers] = useState([]); 

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

    return (
        <div className="container">
            <div className="main_bg">
                <h1 style={{color:'black',display:'none'}}>Built by Zohaib Iqbal, BC200204155</h1>
                <div className="chat_list">
                    <h1 className='Greet' style={{ textAlign: 'center' }}>Hey, {username}</h1>
                    {registeredUsers.map((user, index) => (
                        <NavLink
                            to={`/Interface/${user.username}`}
                            key={index}
                            className="chat_item active"
                            // activeClassName="active" // 
                        >
                            <div className="chat_details">
                                <img
                                    src={user.profile_photo} 
                                    style={{ width: '50px', borderRadius: '100px' }}
                                    alt={user.username}
                                    className="avatar"
                                />
                                <div className="profile">
                                    <h1 style={{ color: 'whitesmoke', fontWeight: '400' }} className="contact_name">{user.username}</h1>
                                    <p className="last_message">{user.email}</p>
                                </div>
                            </div>
                        </NavLink>
                    ))}
                </div>
            </div>
        </div>
    );
};
