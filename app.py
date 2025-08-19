from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import sqlite3
import os
DB_PATH = 'messages.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        encrypted TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()
init_db()

def save_message(username, encrypted, timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO messages (username, encrypted, timestamp) VALUES (?, ?, ?)',
              (username, encrypted, timestamp))
    conn.commit()
    conn.close()

def get_messages(limit=50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT username, encrypted, timestamp FROM messages ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows[::-1]

app = Flask(__name__, static_folder='.', template_folder='.')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

users = set()
user_sid_map = {}
room = 'main_room'


@app.route('/')
def index():
    return app.send_static_file('index.html')

# Endpoint to get message history
@app.route('/history')
def history():
    messages = get_messages()
    return jsonify([
        {'username': u, 'encrypted': e, 'timestamp': t} for u, e, t in messages
    ])

@socketio.on('join')
def handle_join(data):
    username = data.get('username')
    sid = request.sid
    # Only allow two users in the room at a time
    if sid in user_sid_map:
        print(f'[BACKEND] {username} already joined (sid={sid})')
        emit('status', {'msg': f'{username} already joined.'}, room=sid)
        return
    if len(user_sid_map) >= 2:
        print(f'[BACKEND] Room full: rejecting {username} (sid={sid})')
        emit('status', {'msg': 'Room full.'}, room=sid)
        disconnect(sid)
        print(f'[BACKEND] Disconnected {username} (sid={sid}) due to room full')
        return
    if username in users:
        print(f'[BACKEND] Username {username} already in use (sid={sid})')
        emit('status', {'msg': f'Username {username} already in use.'}, room=sid)
        disconnect(sid)
        print(f'[BACKEND] Disconnected {username} (sid={sid}) due to duplicate username')
        return
    # Only add/join/send history for valid users
    print(f'[BACKEND] {username} joined (sid={sid})')
    users.add(username)
    user_sid_map[sid] = username
    join_room(room)
    emit('status', {'msg': f'{username} joined.'}, room=room)
    # Send message history to the user who joined
    messages = get_messages()
    socketio.emit('history', [
        {'username': u, 'encrypted': e, 'timestamp': t} for u, e, t in messages
    ], room=sid)
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    username = user_sid_map.get(sid)
    print(f'[BACKEND] Disconnect event for sid={sid}, username={username}')
    if username and username in users:
        users.remove(username)
        del user_sid_map[sid]
        emit('status', {'msg': f'{username} left.'}, room=room)
        print(f'[BACKEND] {username} removed from room (sid={sid})')

@socketio.on('message')
def handle_message(data):
    # Only allow messages from users in the room
    sid = request.sid
    if sid not in user_sid_map:
        emit('status', {'msg': 'You are not in the room.'}, room=sid)
        disconnect(sid)
        return
    encrypted = data.get('encrypted')
    timestamp = data.get('timestamp')
    username = data.get('username')
    if not (encrypted and timestamp and username):
        emit('status', {'msg': 'Invalid message: missing fields.'}, room=sid)
        return
    save_message(username, encrypted, timestamp)
    emit('message', data, room=room)

@socketio.on('public_key')
def handle_public_key(data):
    sid = request.sid
    if sid not in user_sid_map:
        return  # Ignore if user not in room
    # Relay the public key to the other user in the room
    for other_sid, other_username in user_sid_map.items():
        if other_sid != sid:
            emit('public_key', data, room=other_sid)
            break

if __name__ == '__main__':
    # Auto-port selection for different environments
    port = int(os.environ.get('PORT', 5000))  # Use PORT env var for containers
    ports_to_try = [port] if port != 5000 else [5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010]
    
    for port in ports_to_try:
        try:
            print(f'Starting server on port {port}')
            socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
            break
        except OSError as e:
            if "Address already in use" in str(e) and port != ports_to_try[-1]:
                print(f'Port {port} is in use, trying next port...')
                continue
            else:
                raise
