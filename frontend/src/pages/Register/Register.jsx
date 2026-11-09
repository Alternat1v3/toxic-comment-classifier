//  Built by "Zohaib Iqbal" CS619
//  Contact: Zohaibiqbal639@gmail.com, bc200204155@vu.edu.pk
import React, { useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie'; 
import '../Register/Register.css';

const Register = ({ onRegister }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [profilePhoto, setProfilePhoto] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('email', email);
      formData.append('password', password);
      formData.append('profile_photo', profilePhoto);

      const csrfToken = Cookies.get('csrftoken');

      const response = await axios.post('http://127.0.0.1:8000/register', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRFToken': csrfToken, 
        },
        withCredentials: true, 
      });

      console.log('Registration successful:', response.data);
      onRegister();
    } catch (error) {
      console.log(error.response.data);
      console.error('Registration error:', error);
      setErrorMessage('Registration failed. Please try again.');
    }
  };

  return (
    <div className="body">
      <div className='wrapper'>
        <h1 style={{color:'black'}}>Built by Zohaib Iqbal, (BC200204155)</h1>
        <h2>Registration</h2>
        {errorMessage && <p>{errorMessage}</p>}
        <form onSubmit={handleSubmit}>
          <div className='input-box'>
            <label>Username:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className='input-box'>
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className='input-box'>
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className='input-box'>
            <label>Confirm Password:</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          <div className='input-box'>
            <label>Profile Photo:</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setProfilePhoto(e.target.files[0])}
              required
            />
          </div>
          <div className="input-box button">
            <input type="submit" value="Register Now" />
          </div>
        </form>
        <p>
          Already have an account? Click{' '}
          <span
            style={{ color: 'blue', cursor: 'pointer' }}
            onClick={() => onRegister()}
          >
            Here
          </span>{' '}
          to log in.
        </p>
      </div>
    </div>
  );
};

export default Register;

// import React, { useState } from 'react';
// import axios from 'axios';
// import '../Register/Register.css'

// const Register = ({ onRegister }) => {
//   const [username, setUsername] = useState('');
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [confirmPassword, setConfirmPassword] = useState('');
//   const [profilePhoto, setProfilePhoto] = useState(null);
//   const [errorMessage, setErrorMessage] = useState('');

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (password !== confirmPassword) {
//       setErrorMessage('Passwords do not match');
//       return;
//     }
//     try {
//       const formData = new FormData();
//       formData.append('username', username);
//       formData.append('email', email);
//       formData.append('password', password);
//       formData.append('profile_photo', profilePhoto);

//       const response = await axios.post('http://127.0.0.1:8000/register', formData, {
//         headers: {
//           'Content-Type': 'multipart/form-data',
//         },
//       });
//       console.log('Registration successful:', response.data);
//       onRegister();
//     } catch (error) {
//       console.log(error.response.data);
//       console.error('Registration error:', error);
//       setErrorMessage('Registration failed. Please try again.');
//     }
//   };

//   return (
//     <div className="body">
//     <div className='wrapper'>
//       <h1 style={{color:'black'}}>Built by Zohaib Iqbal, (BC200204155)</h1>
//       <h2>Registration</h2>
//       {errorMessage && <p>{errorMessage}</p>}
//       <form onSubmit={handleSubmit}>
//         <div className='input-box'>
//           <label>Username:</label>
//           <input
//             type="text"
//             alue={username}
//             onChange={(e) => setUsername(e.target.value)}
//             required
//           />
//         </div>
//         <div className='input-box'>
//           <label>Email:</label>
//           <input
//             type="email"
//             value={email}
//             onChange={(e) => setEmail(e.target.value)}
//             required
//           />
//         </div>
//         <div className='input-box'>
//           <label>Password:</label>
//           <input
//             type="password"
//             value={password}
//             onChange={(e) => setPassword(e.target.value)}
//             required
//           />
//         </div>
//         <div className='input-box'>
//           <label>Confirm Password:</label>
//           <input
//             type="password"
//             value={confirmPassword}
//             onChange={(e) => setConfirmPassword(e.target.value)}
//             required
//           />
//         </div>
//         <div className='input-box'>
//           <label>Profile Photo:</label>
//           <input
//             type="file"
//             accept="image/*"
//             onChange={(e) => setProfilePhoto(e.target.files[0])}
//             required
//           />
//         </div>
//         <div className="input-box button">
//           <input type="submit" value="Register Now" />
//         </div>
//       </form>
//       <p>
//         Already have an account? Click{' '}
//         <span
//           style={{ color: 'blue', cursor: 'pointer' }}
//           onClick={() => onRegister()}
//         >
//           Here
//         </span>{' '}
//         to log in.
//       </p>
//     </div>
//     </div>
//   );
// };
//       // <h1 style={{color:'black'}}>Built by Zohaib Iqbal, (BC200204155)</h1>
// export default Register;
