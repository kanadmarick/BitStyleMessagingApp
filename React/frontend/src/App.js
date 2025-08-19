
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
    <div className="App" style={{ background: '#000', color: '#00FF00', fontFamily: 'monospace', height: '100vh' }}>
      {!loggedIn ? (
        <form className="login" onSubmit={handleLogin} style={{ margin: '20px auto', background: '#000', border: '2px solid #00FF00', padding: 16, color: '#00FF00', maxWidth: 350 }}>
          <div style={{ textAlign: 'center', marginBottom: 20 }}>
            <canvas id="banner" width="280" height="48" style={{ display: 'block', margin: '0 auto' }}></canvas>
            <div style={{ fontFamily: 'monospace', fontSize: 24, color: '#00FF00', marginTop: 8, letterSpacing: '2px', textShadow: '2px 2px #008800' }}>ByteChat</div>
          </div>
          <input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" className="pixel-input" style={{ width: '100%', marginBottom: 12, padding: '16px 12px', background: '#000', color: '#00FF00', border: '1px solid #00FF00', boxSizing: 'border-box' }} />
          <button type="submit" className="pixel-btn" style={{ width: '100%', padding: '16px 32px', background: '#000', color: '#00FF00', border: '1px solid #00FF00', marginTop: 16 }}>Login</button>
        </form>
      ) : (
        <div className="chat-container" style={{ background: '#000', border: '2px solid #00FF00', height: '100vh', display: 'flex', flexDirection: 'column' }}>
          <div className="messages" style={{ flex: 1, overflowY: 'auto', padding: 12, fontSize: 11, background: '#000', color: '#00FF00', borderBottom: '1px solid #00FF00' }}>
            {messages.map((msg, idx) => (
              <div key={idx} style={{ marginBottom: 12, padding: '4px 8px', background: '#191970', border: '2px solid #FFD700', color: '#FFD700', boxShadow: '2px 2px #8B008B', fontSize: 13 }}>
                <span style={{ display: 'inline-block', width: 16, height: 16, background: getUserColor(msg.user), borderRadius: 3, marginRight: 6 }}></span>
                <strong style={{ color: '#00FFFF', marginRight: 8 }}>{msg.user}</strong>
                <span style={{ color: '#aaa', fontSize: 10 }}>{formatTimestamp(msg.timestamp)}</span>: {msg.text}
              </div>
            ))}
          </div>
          <div className="input-area" style={{ display: 'flex', alignItems: 'center', gap: 12, borderTop: '1px solid #00FF00', padding: 12, background: '#000' }}>
            <input type="text" value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSend()} placeholder="Type a message..." style={{ flex: 1, fontFamily: 'monospace', fontSize: 13, background: '#000', color: '#00FF00', border: '1px solid #00FF00', padding: '12px 16px' }} />
            <button onClick={handleSend} style={{ fontFamily: 'monospace', fontSize: 13, background: '#000', color: '#00FF00', border: '1px solid #00FF00', padding: '0 24px' }}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
