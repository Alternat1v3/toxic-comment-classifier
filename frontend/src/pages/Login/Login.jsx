import React, { useState } from 'react';
import axios from 'axios';

function Login({ onLogin }) {
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://127.0.0.1:8000/login/', formData, { withCredentials: true });
            const { username } = formData;
            onLogin(username); 
            console.log('Login successful');
        } catch (error) {
            console.error('Login failed:', error.response.data);
            setError('Invalid username or password');
        }
    };

    return (
        <div className="body">
        <div className='wrapper'>
            <h2>Login</h2>
            {error && <div style={{ color: 'red' }}>{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className="input-box">
                    <label>Username:</label>
                    <input type="text" name="username" value={formData.username} onChange={handleChange} />
                </div>
                <div className="input-box">
                    <label>Password:</label>
                    <input type="password" name="password" value={formData.password} onChange={handleChange} />
                </div>
                <div class="input-box button">
                    <input type="submit" value="Login Now" />
                </div>
                <div class="text">
                <h3>
                    Don't have an account?
                    <a style={{textDecoration:'none'}} href="http://localhost:3000/register"> Register Now</a>
                </h3>
                </div>
            </form>
      </div>
        </div>
    );
}

export default Login;
