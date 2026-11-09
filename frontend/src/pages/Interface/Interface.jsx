import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import '../Interface/Interface.css';
import { IoIosSend } from "react-icons/io";
import { FaVideo } from "react-icons/fa";
import { IoIosCall } from "react-icons/io";

export const Interface = ({ contacts, username,isDarkMode }) => {
    const { id } = useParams();
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);
    const [socket, setSocket] = useState(null);
    const messagesEndRef = useRef(null); 
    const messagesContainerRef = useRef(null); 

    useEffect(() => {

        const newSocket = new WebSocket(`ws://localhost:8000/ws/chat/${username}/${id}/`);
        newSocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            setMessages((prevMessages) => [...prevMessages, data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp)));
        };

        setSocket(newSocket);

        return () => {
            newSocket.close();
            setMessages([]); 
        };
    }, [id, username]);

    useEffect(() => {
     
        if (messagesContainerRef.current) {
            messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
        }
    }, [messages]);

    const contact = contacts.find(c => c.username === id);
    if (!contact) return <div>Contact not found</div>;

  
    const sendMessage = () => {
        if (socket) {
            socket.send(JSON.stringify({
                'message': message,
                'sender': username,
                'timestamp': new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
            }));
            setMessage('');
        }
    };

    
    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); 
            sendMessage();
        }
    };

    const iconColor = isDarkMode ? 'white' : 'black' 
    return (
        <div className="container" style={{ width: "100%" }}>
            <div className="chat-interface" style={{ width: '100%' }}>
                <div className="header">
                    <div className="header_left">
                        <img src={contact.profile_photo} alt="" />
                        <h1>{contact.username}</h1>
                    </div>
                    <div className="icona">
                        <button><FaVideo color={iconColor}/></button>
                        <button><IoIosCall color={iconColor}/></button>
                    </div>
                </div>
                <div className="messages" ref={messagesContainerRef}>
                    {messages.map((msg, index) =>
                        <div 
                            className={`msg ${msg.sender === username ? "sent" : "received"}`} 
                            key={index}
                        >
                            <div>
                                {msg.message}
                            </div>
                            <div className="timestamp">
                                {msg.timestamp}
                            </div>
                        </div>
                    )}
                </div>
                <div className="input-area">
                    <input
                        type="text"
                        placeholder="Type a message..."
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyUp={handleKeyPress}
                    />
                    <button style={{margin:'0px'}} onClick={sendMessage}><IoIosSend style={{fontSize:'25px'}}/></button>
                </div>
            </div>
        </div>
    );
};
