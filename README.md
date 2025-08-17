# Bit Style Messaging App Documentation

## Overview
This is a web-based messaging app for two users, featuring a pixel-art (bit style) theme and end-to-end encryption. The backend is built with Python (Flask + Flask-SocketIO), and the frontend uses HTML, CSS, and JavaScript with CryptoJS for encryption.

---

## Files
- `app.py`: Python backend server
- `index.html`: Frontend UI and client logic
- `test_app.py`, `test_app_detailed.py`: Unit tests for backend functionality

---

## Functionality

### 1. User Login
- Users enter a username and a shared room key.
- Only two users can join the chat room at a time.
- The room key is used for AES encryption/decryption of messages.

### 2. Pixel-Art Chat UI
- Uses the 'Press Start 2P' font and neon colors for a retro, pixel-art look.
- Chat interface includes a message display area and input box.

### 3. End-to-End Encryption
- Messages are encrypted in the browser using AES (CryptoJS) before being sent.
- The backend relays encrypted messages; it never sees plaintext.
- On receipt, messages are decrypted in the browser using the room key.

### 4. Real-Time Messaging
- Uses Flask-SocketIO for real-time communication via WebSockets.
- Messages and status updates are broadcast to both users in the room.

### 5. Room Limit
- The backend enforces a two-user limit per room.
- If a third user tries to join, they receive a "Room full" message.

### 6. Unit Testing
- `test_app.py` checks basic route and server response.
- `test_app_detailed.py` tests join events, room limit, and message relay.

---

## How It Works

### Frontend (`index.html`)
- On login, connects to the backend via Socket.IO.
- Encrypts outgoing messages with the room key.
- Decrypts incoming messages with the room key.
- Displays messages in a styled chat window.

### Backend (`app.py`)
- Serves the static HTML frontend.
- Handles Socket.IO events:
  - `join`: Adds user to the room if space is available.
  - `message`: Relays encrypted messages to all users in the room.
  - Enforces two-user limit.

---

## Security Notes
- The room key must be shared securely between users.
- The backend never sees or stores plaintext messages.
- Encryption is handled entirely in the browser.

---

## Running & Testing
1. Install dependencies: `flask`, `flask-socketio`, `pytest` (already installed).
2. Start the server: `python app.py`
3. Open `index.html` in your browser (served by Flask).
4. Run tests: `python -m unittest test_app.py` or `python -m unittest test_app_detailed.py`

---

## Extending
- You can add more features (e.g., avatars, message history, notifications) by updating the frontend and backend.
- For more users, update the room logic in `app.py`.

---

## Contact
For questions or improvements, open an issue or pull request on your GitHub repository.
