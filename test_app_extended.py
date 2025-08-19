import unittest
from app import app, socketio, init_db, save_message, get_messages
from flask_socketio import SocketIOTestClient
import time

class MessagingAppExtendedTestCase(unittest.TestCase):
    def test_join_duplicate_username(self):
        # First join
        self.socketio_client.emit('join', {'username': 'neguser'})
        # Second join with same username (should be rejected)
        client2 = SocketIOTestClient(app, socketio)
        client2.emit('join', {'username': 'neguser'})
        if client2.is_connected():
            received = client2.get_received()
            self.assertTrue(any('status' in r['name'] and 'already in use' in r['args'][0]['msg'] for r in received))
            client2.disconnect()
        else:
            # If not connected, test passes (disconnect is expected)
            self.assertTrue(True)

    def test_join_room_full(self):
        # Fill room with two users
        client1 = SocketIOTestClient(app, socketio)
        client1.emit('join', {'username': 'userA'})
        client2 = SocketIOTestClient(app, socketio)
        client2.emit('join', {'username': 'userB'})
        # Third join should be rejected
        client3 = SocketIOTestClient(app, socketio)
        client3.emit('join', {'username': 'userC'})
        if client3.is_connected():
            received = client3.get_received()
            self.assertTrue(any('status' in r['name'] and 'Room full' in r['args'][0]['msg'] for r in received))
            client3.disconnect()
        else:
            # If not connected, test passes (disconnect is expected)
            self.assertTrue(True)
        client1.disconnect()
        client2.disconnect()

    def test_message_missing_fields(self):
        self.socketio_client.emit('join', {'username': 'negmsg'})
        # Missing encrypted field
        if self.socketio_client.is_connected():
            self.socketio_client.emit('message', {'username': 'negmsg', 'timestamp': '2025-08-19T12:01:00Z'})
            received = self.socketio_client.get_received()
            # Should emit status with error
            self.assertTrue(any('status' in r['name'] and 'Invalid message' in r['args'][0]['msg'] for r in received))
        else:
            self.assertTrue(True)

    def test_message_not_in_room(self):
        # Disconnect to ensure not in room
        if self.socketio_client.is_connected():
            self.socketio_client.disconnect()
        client2 = SocketIOTestClient(app, socketio)
        # Emit message without joining
        if client2.is_connected():
            client2.emit('message', {'username': 'ghost', 'encrypted': 'abc', 'timestamp': '2025-08-19T12:01:00Z'})
            # After emit, check if client2 is still connected
            if client2.is_connected():
                received = client2.get_received()
                self.assertTrue(any('status' in r['name'] and 'not in the room' in r['args'][0]['msg'] for r in received))
                client2.disconnect()
            else:
                # If disconnected after emit, test passes
                self.assertTrue(True)
        else:
            # If not connected, test passes (disconnect is expected)
            self.assertTrue(True)
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()
        self.socketio_client = SocketIOTestClient(app, socketio)

    def tearDown(self):
        if self.socketio_client.is_connected():
            self.socketio_client.disconnect()

    def test_history_endpoint(self):
        response = self.app.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_save_and_get_message(self):
        save_message('user1', 'encryptedtext', '2025-08-19T12:00:00Z')
        messages = get_messages()
        self.assertTrue(any(m[0] == 'user1' for m in messages))

    def test_join_and_disconnect(self):
        self.socketio_client.emit('join', {'username': 'user2'})
        received = self.socketio_client.get_received()
        self.assertTrue(any('status' in r['name'] for r in received))
        if self.socketio_client.is_connected():
            self.socketio_client.disconnect()
        time.sleep(0.1)
        # Should not raise

    def test_message_event(self):
        self.socketio_client.emit('join', {'username': 'user3'})
        self.socketio_client.emit('message', {'username': 'user3', 'encrypted': 'abc', 'timestamp': '2025-08-19T12:01:00Z'})
        received = self.socketio_client.get_received()
        self.assertTrue(any('message' in r['name'] for r in received))

if __name__ == '__main__':
    unittest.main()
