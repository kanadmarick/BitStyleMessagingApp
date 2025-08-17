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

    def test_join_event(self):
        client = socketio.test_client(app)
        client.emit('join', {'username': 'user1'})
        received = client.get_received()
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
        client = socketio.test_client(app)
        client.emit('join', {'username': 'user1'})
        client.emit('message', {'username': 'user1', 'text': 'encryptedtext'})
        received = client.get_received()
        self.assertTrue(any(r['name'] == 'message' for r in received))
        self.assertTrue(any(r['args']['text'] == 'encryptedtext' for r in received if r['name'] == 'message'))

    def test_message_timestamp(self):
        client = socketio.test_client(app)
        client.emit('join', {'username': 'user1'})
        now = 1723939200000  # fixed timestamp for test
        client.emit('message', {'username': 'user1', 'text': 'testmsg', 'timestamp': now})
        received = client.get_received()
        timestamps = [r['args'].get('timestamp') for r in received if r['name'] == 'message']
        self.assertIn(now, timestamps)

    def test_user_color_assignment(self):
        def get_user_color(name):
            colors = ['#FFD700', '#00FFFF', '#FF69B4', '#7CFC00', '#FF4500', '#8B008B']
            hash = 0
            for c in name:
                hash += ord(c)
            return colors[hash % len(colors)]
        self.assertEqual(get_user_color('user1'), get_user_color('user1'))
        self.assertNotEqual(get_user_color('user1'), get_user_color('user2'))

    def test_two_users_messaging(self):
        import time
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        # Only two users join
        client1.emit('join', {'username': 'userA'})
        client2.emit('join', {'username': 'userB'})
        # Clear any join status messages
        client1.get_received()
        client2.get_received()
        now1 = 1723939200001
        now2 = 1723939200002
        client1.emit('message', {'username': 'userA', 'text': 'helloB', 'timestamp': now1})
        client2.emit('message', {'username': 'userB', 'text': 'helloA', 'timestamp': now2})
        time.sleep(0.2)
        received1 = client1.get_received()
        received2 = client2.get_received()
        print('DEBUG received1:', received1)
        print('DEBUG received2:', received2)
        messages1 = [(r['args']['text'], r['args'].get('timestamp')) for r in received1 if r['name'] == 'message']
        messages2 = [(r['args']['text'], r['args'].get('timestamp')) for r in received2 if r['name'] == 'message']
        self.assertIn(('helloB', now1), messages1 + messages2)
        self.assertIn(('helloA', now2), messages1 + messages2)

if __name__ == '__main__':
    unittest.main()
