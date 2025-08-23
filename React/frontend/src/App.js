
import React, { useState, useRef, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

function getUserColor(name) {
  const colors = ['#00FF00', '#00CC00', '#009900', '#00AA00', '#008800', '#00DD00'];
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash += name.charCodeAt(i);
  return colors[hash % colors.length];
}

function formatTimestamp(ts) {
  if (!ts) return '';
  const d = new Date(ts);
  return `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
}

function App() {
  const [username, setUsername] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState('');
  const [sharedKey, setSharedKey] = useState(null);
  const socketRef = useRef(null);
  const keyPairRef = useRef(null);

  useEffect(() => {
    if (loggedIn) {
      // Try to connect to backend on multiple ports
      const backendPorts = [5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010];
      let connected = false;
      
      const tryConnection = async (portIndex = 0) => {
        if (portIndex >= backendPorts.length || connected) return;
        
        const port = backendPorts[portIndex];
        console.log(`Trying to connect to backend on port ${port}`);
        
        // Fetch message history
        fetch(`http://localhost:${port}/history`)
          .then(response => response.json())
          .then(history => {
            setMessages(history.map(msg => ({
              user: msg.username,
              text: msg.encrypted,
              timestamp: msg.timestamp
            })));
          })
          .catch(error => console.error('Error fetching history:', error));

        socketRef.current = io(`http://localhost:${port}`, {
          timeout: 2000,
          forceNew: true
        });
        
        socketRef.current.on('connect', () => {
          console.log(`Connected to backend on port ${port}`);
          connected = true;
          addMessage('System', `Connected to backend on port ${port}`);
          
          // Join the room immediately after connection
          socketRef.current.emit('join', { username });
          
          // Set up message listeners after connection
          socketRef.current.on('message', async function(data) {
            if (sharedKey && data.iv && data.text) {
              try {
                const iv = new Uint8Array(atob(data.iv).split('').map(c => c.charCodeAt(0)));
                const encryptedData = new Uint8Array(atob(data.text).split('').map(c => c.charCodeAt(0)));
                const decryptedArrayBuffer = await window.crypto.subtle.decrypt(
                  { name: 'AES-GCM', iv: iv },
                  sharedKey,
                  encryptedData
                );
                const decrypted = new TextDecoder().decode(decryptedArrayBuffer);
                addMessage(data.username, decrypted, data.timestamp);
              } catch (e) {
                addMessage('System', 'Error decrypting message.');
              }
            } else if (data.text) {
              addMessage(data.username, data.text, data.timestamp);
            }
          });

          socketRef.current.on('status', function(data) {
            addMessage('System', data.msg);
          });

          socketRef.current.on('public_key', async (data) => {
            const remotePublicKey = await window.crypto.subtle.importKey(
              'jwk',
              data.key,
              { name: 'ECDH', namedCurve: 'P-256' },
              true,
              []
            );
            const derivedKey = await window.crypto.subtle.deriveKey(
              { name: 'ECDH', public: remotePublicKey },
              keyPairRef.current.privateKey,
              { name: 'AES-GCM', length: 256 },
              true,
              ['encrypt', 'decrypt']
            );
            setSharedKey(derivedKey);
            addMessage('System', 'Secure connection established.');
          });
          
          // Generate key pair for encryption (optional for single user)
          window.crypto.subtle.generateKey(
            { name: 'ECDH', namedCurve: 'P-256' },
            true,
            ['deriveKey']
          ).then(keyPair => {
            keyPairRef.current = keyPair;
            window.crypto.subtle.exportKey('jwk', keyPair.publicKey).then(publicKeyJwk => {
              socketRef.current.emit('public_key', { key: publicKeyJwk });
            });
          });
        });
        
        socketRef.current.on('connect_error', () => {
          console.log(`Failed to connect to port ${port}`);
          socketRef.current.disconnect();
          setTimeout(() => tryConnection(portIndex + 1), 500);
        });
      };
      
      tryConnection(0);

      return () => {
        if (socketRef.current) {
          socketRef.current.disconnect();
        }
      };
    }
    // eslint-disable-next-line
  }, [loggedIn]); // Remove sharedKey dependency to avoid recreating listeners

  function addMessage(user, text, timestamp) {
    setMessages(msgs => [...msgs, { user, text, timestamp }]);
  }

  async function handleSend() {
    if (!input.trim()) return;
    const now = Date.now();
    if (sharedKey) {
      const iv = window.crypto.getRandomValues(new Uint8Array(12));
      const encodedText = new TextEncoder().encode(input);
      const encryptedArrayBuffer = await window.crypto.subtle.encrypt(
        { name: 'AES-GCM', iv: iv },
        sharedKey,
        encodedText
      );
      const encrypted = btoa(String.fromCharCode.apply(null, new Uint8Array(encryptedArrayBuffer)));
      const ivString = btoa(String.fromCharCode.apply(null, iv));
      socketRef.current.emit('message', { username, text: encrypted, iv: ivString, timestamp: now });
    } else {
      // Send plaintext if no sharedKey (single user mode)
      socketRef.current.emit('message', { username, text: input, timestamp: now });
    }
    setInput('');
  }

  function handleLogin(e) {
    e.preventDefault();
    if (username.trim()) {
      setLoggedIn(true);
    }
  }

  return (
    <div className="App">
      {!loggedIn ? (
        <form className="login" onSubmit={handleLogin}>
          <div>
            <canvas id="banner" width="280" height="48"></canvas>
            <div className="login-title">ByteChat</div>
          </div>
          <input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" className="pixel-input" />
          <button type="submit" className="pixel-btn">Login</button>
        </form>
      ) : (
        <div className="chat-container">
          <div className="messages">
            {messages.map((msg, idx) => (
              <div key={idx} className="message">
                <span className="user-avatar" style={{ backgroundColor: getUserColor(msg.user) }}></span>
                <strong className="message-user">{msg.user}</strong>
                <span className="message-timestamp">{formatTimestamp(msg.timestamp)}</span>: {msg.text}
              </div>
            ))}
          </div>
          <div className="input-area">
            <input type="text" value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSend()} placeholder="Type a message..." />
            <button onClick={handleSend}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
