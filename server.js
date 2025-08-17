// Minimal WebSocket relay with 2‑person room cap. Run: `node server.js`
// Dependencies: npm i ws
const http = require('http');
const WebSocket = require('ws');

const server = http.createServer();
const wss = new WebSocket.Server({ server });

const rooms = new Map(); // roomId -> Set of sockets

function broadcast(room, data, except=null){
  const set = rooms.get(room);
  if(!set) return;
  for(const ws of set){ if(ws !== except && ws.readyState === WebSocket.OPEN){ ws.send(JSON.stringify(data)); } }
}

wss.on('connection', (ws) => {
  ws.meta = { room:null, name:null };

  ws.on('message', (buf) => {
    let msg = null; try{ msg = JSON.parse(buf.toString()); } catch{ return; }
    const { t } = msg;

    if(t === 'join'){
      const room = String(msg.room || '').slice(0,32);
      ws.meta.room = room; ws.meta.name = String(msg.name||'Anon').slice(0,32);
      if(!rooms.has(room)) rooms.set(room, new Set());
      const set = rooms.get(room);
      if(set.size >= 2){
        ws.send(JSON.stringify({ t:'error', text:'Room is full (2 users max).'}));
        ws.close();
        return;
      }
      set.add(ws);
      broadcast(room, { t:'sys', text:`[${ws.meta.name} joined]` }, null);
      // Clean up on close
      ws.on('close', () => {
        const s = rooms.get(room);
        if(s){ s.delete(ws); if(s.size === 0) rooms.delete(room); }
        broadcast(room, { t:'sys', text:`[${ws.meta.name} left]` }, null);
      });
      return;
    }

    if(t === 'pubkey'){
      const room = ws.meta.room; if(!room) return;
      // Relay the public key to the other peer(s) without storing it
      broadcast(room, { t:'pubkey', pub: msg.pub }, ws);
      return;
    }

    if(t === 'msg'){
      const room = ws.meta.room; if(!room) return;
      // Relay encrypted payload as‑is (server never sees plaintext)
      broadcast(room, { t:'msg', payload: msg.payload }, ws);
      return;
    }
  });
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => console.log(`TwoBitChat relay listening on ws://localhost:${PORT}`));
// Minimal WebSocket relay with 2‑person room cap. Run: `node server.js`
// Dependencies: npm i ws
const http = require('http');
const WebSocket = require('ws');

const server = http.createServer();
const wss = new WebSocket.Server({ server });

const rooms = new Map(); // roomId -> Set of sockets

function broadcast(room, data, except=null){
  const set = rooms.get(room);
  if(!set) return;
  for(const ws of set){ if(ws !== except && ws.readyState === WebSocket.OPEN){ ws.send(JSON.stringify(data)); } }
}

wss.on('connection', (ws) => {
  ws.meta = { room:null, name:null };

  ws.on('message', (buf) => {
    let msg = null; try{ msg = JSON.parse(buf.toString()); } catch{ return; }
    const { t } = msg;

    if(t === 'join'){
      const room = String(msg.room || '').slice(0,32);
      ws.meta.room = room; ws.meta.name = String(msg.name||'Anon').slice(0,32);
      if(!rooms.has(room)) rooms.set(room, new Set());
      const set = rooms.get(room);
      if(set.size >= 2){
        ws.send(JSON.stringify({ t:'error', text:'Room is full (2 users max).'}));
        ws.close();
        return;
      }
      set.add(ws);
      broadcast(room, { t:'sys', text:`[${ws.meta.name} joined]` }, null);
      // Clean up on close
      ws.on('close', () => {
        const s = rooms.get(room);
        if(s){ s.delete(ws); if(s.size === 0) rooms.delete(room); }
        broadcast(room, { t:'sys', text:`[${ws.meta.name} left]` }, null);
      });
      return;
    }

    if(t === 'pubkey'){
      const room = ws.meta.room; if(!room) return;
      // Relay the public key to the other peer(s) without storing it
      broadcast(room, { t:'pubkey', pub: msg.pub }, ws);
      return;
    }

    if(t === 'msg'){
      const room = ws.meta.room; if(!room) return;
      // Relay encrypted payload as‑is (server never sees plaintext)
      broadcast(room, { t:'msg', payload: msg.payload }, ws);
      return;
    }
  });
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => console.log(`TwoBitChat relay listening on ws://localhost:${PORT}`));
