from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect

app = Flask(__name__, static_folder='.', template_folder='.')
app.config['SECRET_KEY'] = 'secret!'
# Allow all origins for testing compatibility
socketio = SocketIO(app, cors_allowed_origins='*')

users = set()
user_sid_map = {}
room = 'main_room'

@app.route('/')
def index():
    return app.send_static_file('index.html')

@socketio.on('join')
def handle_join(data):
    username = data.get('username')
    sid = request.sid
    if len(users) < 2:
        users.add(username)
        user_sid_map[sid] = username
        join_room(room)
        emit('status', {'msg': f'{username} joined.'}, room=room)
    else:
        emit('status', {'msg': 'Room full.'})
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    username = user_sid_map.get(sid)
    if username and username in users:
        users.remove(username)
        del user_sid_map[sid]
        emit('status', {'msg': f'{username} left.'}, room=room)

@socketio.on('message')
def handle_message(data):
    emit('message', data, room=room)

if __name__ == '__main__':
    import sys
    import socket
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except Exception:
            pass
    # Try to bind to the chosen port, else find a free one
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            sock.bind(('0.0.0.0', port))
            sock.close()
            break
        except OSError:
            port += 1
    print(f"Starting server on port {port}")
    socketio.run(app, host='0.0.0.0', port=port)
