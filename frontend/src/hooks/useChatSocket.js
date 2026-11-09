import { useCallback, useEffect, useRef, useState } from 'react';
import { chat } from '../api';

// Close codes the server uses on purpose; reconnecting would not help.
const FINAL_CLOSE_CODES = { 4401: 'Your session has ended. Please sign in again.', 4404: 'That user does not exist.' };

/** One WebSocket per conversation: history on connect, then live messages. */
export default function useChatSocket(username) {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const socketRef = useRef(null);

  useEffect(() => {
    if (!username) return undefined;
    let stopped = false;
    let retryTimer;
    let attempt = 0;

    const connect = () => {
      setStatus('connecting');
      const socket = new WebSocket(chat.socketUrl(username));
      socketRef.current = socket;

      socket.onopen = () => {
        attempt = 0;
        setStatus('open');
        setError('');
      };
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'history') setMessages(data.messages);
        else if (data.type === 'message') setMessages((list) => [...list, data.message]);
        else if (data.type === 'error') setError(data.detail);
      };
      socket.onclose = (event) => {
        if (stopped) return;
        if (FINAL_CLOSE_CODES[event.code]) {
          setStatus('closed');
          setError(FINAL_CLOSE_CODES[event.code]);
          return;
        }
        // Lost the connection: try again, waiting a little longer each time (up to 10 s).
        setStatus('reconnecting');
        attempt += 1;
        retryTimer = setTimeout(connect, Math.min(10000, 500 * 2 ** attempt));
      };
    };

    setMessages([]);
    setError('');
    connect();
    return () => {
      stopped = true;
      clearTimeout(retryTimer);
      socketRef.current?.close();
    };
  }, [username]);

  const send = useCallback((text) => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) return false;
    socket.send(JSON.stringify({ message: text }));
    return true;
  }, []);

  return { messages, status, error, send };
}
