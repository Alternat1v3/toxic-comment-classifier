//  Built by "Zohaib Iqbal" CS619
//  Contact: Zohaibiqbal639@gmail.com, bc200204155@vu.edu.pk

import React, { useState } from 'react';
import '../component/Sidebar.css'
import {
    FaTh,
    FaRocketchat,
    FaList,
    FaSearch,
    FaHandPaper,
    FaBars,
    FaHeart,
    FaLock,
    FaRegChartBar,
    FaCommentAlt,
    FaShoppingBag,
    FaThList
}from "react-icons/fa";
import { IoArrowBackSharp,
    IoArrowForward
 } from "react-icons/io5";
import { 
    CiLogout,
    CiSettings,
    CiHeart,
    CiSearch,
    CiViewList,
    CiChat2
 } from "react-icons/ci";
import { BsPersonCircle } from "react-icons/bs";

import { NavLink } from 'react-router-dom';


const Sidebar = ({children}) => {
    const[isOpen ,setIsOpen] = useState(true);
    const toggle = () => setIsOpen (!isOpen);
    const menuItem=[
        {
            path:"/",
            name:"Chat",
            icon:<CiChat2/>
        },
        {
            path:"/Listing",
            name:"Registered Users",
            icon:<CiViewList/>
        },
        {
            path:"/Search Analytics",
            name:"Search Analytics",
            icon:<CiSearch/>
        },
        {
            path:"/My Matches",
            name:"My Matches",
            icon:<FaHandPaper/>
        },
        {
            path:"/My Profile",
            name:"My Profile",
            icon:<BsPersonCircle />
        },
        {
            path:"/Feedback",
            name:"Feedback",
            icon:<CiHeart />
        },
        {
            path:"/Settings",
            name:"Settings",
            icon:<CiSettings />
        },
                {
            path:"/Logout",
            name:"Logout",
            icon:<CiLogout/>
        }
    ]
    return (
        <div className="container">
           <div style={{width: isOpen ? "250px" : "50px"}} className="sidebar">
               <div className="top_section">
                   {/* <h1 style={{display: isOpen ? "none" : "none"}} className="logo">Logo</h1> */} 
                   <div style={{marginLeft: isOpen ? "0px" : "0px",display: isOpen ? "block" : 'none', cursor:'pointer'}} className="bars">
                       <IoArrowBackSharp onClick={toggle}/>
                   </div>
                   <div style={{marginLeft: isOpen ? "50px" : "0px",display: isOpen ? "None" : 'block', cursor:'pointer'}} className="bars">
                       <IoArrowForward onClick={toggle}/>
                   </div>
               </div>
               {
                   menuItem.map((item, index)=>(
                       <NavLink to={item.path} key={index} className="link" activeclassName="active">
                           <div className="icon">{item.icon}</div>
                           <div style={{display: isOpen ? "block" : "none"}} className="link_text">{item.name}</div>
                       </NavLink>
                   ))
               }
           </div>
           <main>{children}</main>
        </div>
    );
};

export default Sidebar;