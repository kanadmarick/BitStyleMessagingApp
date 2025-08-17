import unittest
from app import app, socketio

class MessagingAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bit Style Messaging App', response.data)

    # Additional tests for socket events can be added with Flask-SocketIO's test client

if __name__ == '__main__':
    unittest.main()
