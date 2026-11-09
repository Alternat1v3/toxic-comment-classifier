import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HiArrowRightOnRectangle,
  HiOutlineBeaker,
  HiOutlineChatBubbleBottomCenterText,
  HiOutlineChatBubbleLeftRight,
  HiOutlineCog6Tooth,
} from 'react-icons/hi2';
import Avatar from './Avatar';

const LINKS = [
  { to: '/', label: 'Chats', icon: HiOutlineChatBubbleLeftRight, isActive: (path) => path === '/' || path.startsWith('/chat/') },
  { to: '/moderation', label: 'Moderation lab', icon: HiOutlineBeaker },
  { to: '/feedback', label: 'Feedback', icon: HiOutlineChatBubbleBottomCenterText },
  { to: '/settings', label: 'Settings', icon: HiOutlineCog6Tooth },
];

export default function Layout({ user, onSignOut, children }) {
  const { pathname } = useLocation();

  return (
    <div className="app">
      <nav className="rail" aria-label="Main">
        <div className="rail__brand">
          <span className="logo-mark" aria-hidden="true">S</span>
          <span className="rail__label">SafeChat</span>
        </div>
        <ul className="rail__links">
          {LINKS.map(({ to, label, icon: Icon, isActive }) => {
            const active = isActive ? isActive(pathname) : pathname.startsWith(to);
            return (
              <li key={to}>
                <Link to={to} className={`rail__link${active ? ' is-active' : ''}`} aria-current={active ? 'page' : undefined} title={label}>
                  <Icon aria-hidden="true" />
                  <span className="rail__label">{label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
        <div className="rail__me">
          <Avatar user={user} size={36} />
          <div className="rail__label rail__who">
            <strong>{user.username}</strong>
            <span>{user.toxic_message_count ? `${user.toxic_message_count} flagged` : 'No flagged messages'}</span>
          </div>
          <button className="icon-button" onClick={onSignOut} title="Sign out" aria-label="Sign out">
            <HiArrowRightOnRectangle aria-hidden="true" />
          </button>
        </div>
      </nav>
      <main className="main">{children}</main>
    </div>
  );
}
