import unittest
from flask import Flask
from flask_socketio import SocketIO
from app import app, socketio

class MessagingAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.socketio_test_client = socketio.test_client(app)

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bit Style Messaging App', response.data)

    def test_join_event(self):
        self.socketio_test_client.emit('join', {'username': 'user1'})
        received = self.socketio_test_client.get_received()
        self.assertTrue(any('status' in r['name'] for r in received))

    def test_room_limit(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        client3 = socketio.test_client(app)
        client1.emit('join', {'username': 'user1'})
        client2.emit('join', {'username': 'user2'})
        client3.emit('join', {'username': 'user3'})
        received = client3.get_received()
        self.assertTrue(any('Room full.' in r['args'][0]['msg'] for r in received if r['name'] == 'status'))

    def test_message_event(self):
        # Join the room as user1
        self.socketio_test_client.emit('join', {'username': 'user1'})
        # Send a message
        self.socketio_test_client.emit('message', {'username': 'user1', 'text': 'encryptedtext'})
        # Get received events
        received = self.socketio_test_client.get_received()
        print('DEBUG received:', received)
        # Check for message event
        self.assertTrue(any(r['name'] == 'message' for r in received))

if __name__ == '__main__':
    unittest.main()
