from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__, static_folder='.', template_folder='.')
socketio = SocketIO(app, cors_allowed_origins="*")

users = set()
room = 'main_room'

@app.route('/')
def index():
    return app.send_static_file('index.html')

@socketio.on('join')
def handle_join(data):
    username = data.get('username')
    if len(users) < 2:
        users.add(username)
        join_room(room)
        emit('status', {'msg': f'{username} joined.'}, room=room)
    else:
        emit('status', {'msg': 'Room full.'})

@socketio.on('message')
def handle_message(data):
    emit('message', data, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
