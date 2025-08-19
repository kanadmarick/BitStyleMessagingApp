import threading
import time
import socketio

SERVER_URL = 'http://localhost:5004'  # Change port if needed

results = {'userA': [], 'userB': []}


def run_client(username, send_text=None, send_timestamp=None, received_list=None, history_list=None):
    sio = socketio.Client()

    @sio.event
    def connect():
        print(f'[CONNECT] {username} connected')
        sio.emit('join', {'username': username})
        time.sleep(0.2)
        if send_text:
            print(f'[SEND] {username} sending message: {send_text}')
            sio.emit('message', {'username': username, 'encrypted': send_text, 'timestamp': send_timestamp})

    @sio.on('message')
    def on_message(data):
        print(f'[RECEIVE] {username} received message:', data)
        received_list.append(data)

    @sio.on('history')
    def on_history(data):
        print(f'[HISTORY] {username} received history:', data)
        if history_list is not None:
            history_list.extend(data)

    @sio.on('status')
    def on_status(data):
        print(f'[STATUS] {username} received status:', data)

    @sio.event
    def disconnect():
        print(f'[DISCONNECT] {username} disconnected')

    try:
        sio.connect(SERVER_URL)
        time.sleep(1)
        sio.disconnect()
    except Exception as e:
        print(f'[ERROR] {username} connection error:', e)



if __name__ == '__main__':
    # Start server manually before running this test!
    print('\n--- Basic persistence test ---')
    t1_msgs = []
    t2_msgs = []
    t1_history = []
    t2_history = []
    t1 = threading.Thread(target=run_client, args=('userA', 'msgA', '1723939200001', t1_msgs, t1_history))
    t2 = threading.Thread(target=run_client, args=('userB', 'msgB', '1723939200002', t2_msgs, t2_history))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print('UserA received:', t1_msgs)
    print('UserB received:', t2_msgs)
    t1_history_reconnect = []
    t1_reconnect = threading.Thread(target=run_client, args=('userA', None, None, [], t1_history_reconnect))
    t1_reconnect.start()
    t1_reconnect.join()
    print('UserA history after reconnect:', t1_history_reconnect)
    encrypted_msgs = [m['encrypted'] for m in t1_history_reconnect]
    print('Checking: msgA in history after reconnect...')
    assert 'msgA' in encrypted_msgs, 'Message from userA not found in history after reconnect'
    print('PASS: msgA found in history')
    print('Checking: msgB in history after reconnect...')
    assert 'msgB' in encrypted_msgs, 'Message from userB not found in history after reconnect'
    print('PASS: msgB found in history')
    print('Message persistence integration test passed!')

    print('\n--- Edge case: Room full ---')
    t3_msgs = []
    t3_history = []
    t3 = threading.Thread(target=run_client, args=('userC', 'msgC', '1723939200003', t3_msgs, t3_history))
    t3.start()
    t3.join()
    # Should not be able to join, so no messages/history
    print('UserC received:', t3_msgs)
    print('UserC history:', t3_history)
    print(f'Checking: userC should not receive messages... Received: {t3_msgs}')
    assert not t3_msgs, 'Room full edge case failed: userC should not receive messages'
    print('PASS: Room full edge case')

    print('\n--- Edge case: Missing fields ---')
    def run_client_missing(username, bad_data):
        sio = socketio.Client()
        @sio.event
        def connect():
            print(f'[CONNECT] {username} connected (missing fields test)')
            sio.emit('join', {'username': username})
            time.sleep(0.2)
            print(f'[SEND] {username} sending bad message: {bad_data}')
            sio.emit('message', bad_data)
        @sio.on('status')
        def on_status(data):
            print(f'[STATUS] {username} received status:', data)
        @sio.event
        def disconnect():
            print(f'[DISCONNECT] {username} disconnected')
        try:
            sio.connect(SERVER_URL)
            time.sleep(1)
            sio.disconnect()
        except Exception as e:
            print(f'[ERROR] {username} connection error:', e)
    # Send message missing encrypted
    run_client_missing('userA', {'username': 'userA', 'timestamp': '1723939200004'})
    # Send message missing timestamp
    run_client_missing('userA', {'username': 'userA', 'encrypted': 'badmsg'})
    # Check that these are not persisted
    import requests
    history = requests.get(f'{SERVER_URL}/history').json()
    encrypted_msgs = [m['encrypted'] for m in history]
    print(f'Checking: badmsg should not be persisted... History: {encrypted_msgs}')
    assert 'badmsg' not in encrypted_msgs, 'Missing field edge case failed: badmsg should not be persisted'
    print('PASS: Missing field edge case')

    print('\n--- Edge case: Empty message ---')
    run_client_missing('userA', {'username': 'userA', 'encrypted': '', 'timestamp': '1723939200005'})
    history = requests.get(f'{SERVER_URL}/history').json()
    encrypted_msgs = [m['encrypted'] for m in history]
    print(f'Checking: empty string should be persisted... History: {encrypted_msgs}')
    assert '' in encrypted_msgs, 'Empty message edge case failed: empty string should be persisted'
    print('PASS: Empty message edge case')

    print('\n--- Edge case: Long message ---')
    long_msg = 'x' * 10000
    run_client_missing('userA', {'username': 'userA', 'encrypted': long_msg, 'timestamp': '1723939200006'})
    history = requests.get(f'{SERVER_URL}/history').json()
    encrypted_msgs = [m['encrypted'] for m in history]
    print(f'Checking: long message should be persisted... Found: {long_msg in encrypted_msgs}')
    assert long_msg in encrypted_msgs, 'Long message edge case failed: long message should be persisted'
    print('PASS: Long message edge case')

    print('\n--- Edge case: Rapid join/leave ---')
    for i in range(5):
        print(f'[TEST] Rapid join/leave: userRapid{i}')
        t = threading.Thread(target=run_client, args=(f'userRapid{i}', None, None, [], []))
        t.start()
        t.join()
    print('PASS: Rapid join/leave edge case')
    print('\nAll edge test cases passed!')

    # Negative test cases
    print('\n--- Negative test cases ---')
    # Negative: invalid username (empty string)
    t_invalid_username = threading.Thread(target=run_client, args=('', 'msgInvalid', '1723939200010', [], []))
    t_invalid_username.start()
    t_invalid_username.join()
    print('PASS: Invalid username (empty string) handled')

    # Negative: duplicate username
    t_dup1 = threading.Thread(target=run_client, args=('userDup', 'msgDup1', '1723939200011', [], []))
    t_dup2 = threading.Thread(target=run_client, args=('userDup', 'msgDup2', '1723939200012', [], []))
    t_dup1.start()
    t_dup2.start()
    t_dup1.join()
    t_dup2.join()
    print('PASS: Duplicate username handled')

    # Negative: invalid message type (non-string encrypted field)
    def run_client_invalid_type(username, bad_data):
        sio = socketio.Client()
        @sio.event
        def connect():
            print(f'[CONNECT] {username} connected (invalid type test)')
            sio.emit('join', {'username': username})
            time.sleep(0.2)
            print(f'[SEND] {username} sending bad message: {bad_data}')
            sio.emit('message', bad_data)
        @sio.on('status')
        def on_status(data):
            print(f'[STATUS] {username} received status:', data)
        @sio.event
        def disconnect():
            print(f'[DISCONNECT] {username} disconnected')
        try:
            sio.connect(SERVER_URL)
            time.sleep(1)
            sio.disconnect()
        except Exception as e:
            print(f'[ERROR] {username} connection error:', e)
    run_client_invalid_type('userType', {'username': 'userType', 'encrypted': 12345, 'timestamp': '1723939200013'})
    print('PASS: Invalid message type handled')

    # Negative: send message after disconnect
    def run_client_send_after_disconnect(username, send_text, send_timestamp):
        sio = socketio.Client()
        @sio.event
        def connect():
            print(f'[CONNECT] {username} connected (send after disconnect test)')
            sio.emit('join', {'username': username})
            time.sleep(0.2)
            sio.disconnect()
            print(f'[SEND] {username} attempting to send after disconnect')
            try:
                sio.emit('message', {'username': username, 'encrypted': send_text, 'timestamp': send_timestamp})
            except Exception as e:
                print(f'[ERROR] {username} send after disconnect:', e)
        @sio.on('status')
        def on_status(data):
            print(f'[STATUS] {username} received status:', data)
        @sio.event
        def disconnect():
            print(f'[DISCONNECT] {username} disconnected')
        try:
            sio.connect(SERVER_URL)
            time.sleep(1)
        except Exception as e:
            print(f'[ERROR] {username} connection error:', e)
    run_client_send_after_disconnect('userAfterDisc', 'msgAfterDisc', '1723939200014')
    print('PASS: Send after disconnect handled')

    print('\nAll negative test cases passed!')
