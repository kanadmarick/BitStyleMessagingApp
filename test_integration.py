import threading
import time
import socketio

SERVER_URL = 'http://localhost:5000'  # Change port if needed

results = {'userA': [], 'userB': []}

def run_client(username, send_text=None, send_timestamp=None, received_list=None):
    sio = socketio.Client()

    @sio.event
    def connect():
        print(f'{username} connected')
        sio.emit('join', {'username': username})
        time.sleep(0.2)
        if send_text:
            sio.emit('message', {'username': username, 'text': send_text, 'timestamp': send_timestamp})

    @sio.on('message')
    def on_message(data):
        print(f'{username} received:', data)
        received_list.append(data)

    sio.connect(SERVER_URL)
    time.sleep(1)
    sio.disconnect()

if __name__ == '__main__':
    # Start server manually before running this test!
    t1_msgs = []
    t2_msgs = []
    t1 = threading.Thread(target=run_client, args=('userA', 'helloB', 1723939200001, t1_msgs))
    t2 = threading.Thread(target=run_client, args=('userB', 'helloA', 1723939200002, t2_msgs))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print('UserA received:', t1_msgs)
    print('UserB received:', t2_msgs)
    assert any(m['text'] == 'helloB' for m in t1_msgs + t2_msgs), 'Message from userA not received'
    assert any(m['text'] == 'helloA' for m in t1_msgs + t2_msgs), 'Message from userB not received'
    print('Integration test passed!')
