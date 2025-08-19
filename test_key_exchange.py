import unittest
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import app, socketio

class TestKeyExchange(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server_thread = threading.Thread(target=socketio.run, args=(app,), kwargs={'port': 5000})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        service = ChromeService(ChromeDriverManager().install())
        self.driver1 = webdriver.Chrome(service=service, options=options)
        self.driver2 = webdriver.Chrome(service=service, options=options)
        self.driver3 = webdriver.Chrome(service=service, options=options)
        self.drivers = [self.driver1, self.driver2, self.driver3]

    def tearDown(self):
        for driver in self.drivers:
            driver.quit()

    def test_successful_key_exchange_and_messaging(self):
        # User 1 joins
        self.driver1.get('http://localhost:5000')
        self.driver1.find_element(By.ID, 'username').send_keys('user1')
        self.driver1.find_element(By.TAG_NAME, 'button').click()

        # User 2 joins
        self.driver2.get('http://localhost:5000')
        self.driver2.find_element(By.ID, 'username').send_keys('user2')
        self.driver2.find_element(By.TAG_NAME, 'button').click()

        # Wait for secure connection message
        wait = WebDriverWait(self.driver1, 10)
        wait.until(EC.text_to_be_present_in_element((By.ID, 'messages'), 'Secure connection established.'))
        wait = WebDriverWait(self.driver2, 10)
        wait.until(EC.text_to_be_present_in_element((By.ID, 'messages'), 'Secure connection established.'))

        # User 1 sends a message
        self.driver1.find_element(By.ID, 'messageInput').send_keys('Hello, user2!')
        self.driver1.find_element(By.XPATH, "//button[text()='Send']").click()

        # Check if User 2 received the message
        wait = WebDriverWait(self.driver2, 10)
        wait.until(EC.text_to_be_present_in_element((By.ID, 'messages'), 'Hello, user2!'))
        messages = self.driver2.find_element(By.ID, 'messages').text
        self.assertIn('user1', messages)
        self.assertIn('Hello, user2!', messages)

    def test_third_user_rejected(self):
        # User 1 joins
        self.driver1.get('http://localhost:5000')
        self.driver1.find_element(By.ID, 'username').send_keys('user1')
        self.driver1.find_element(By.TAG_NAME, 'button').click()

        # User 2 joins
        self.driver2.get('http://localhost:5000')
        self.driver2.find_element(By.ID, 'username').send_keys('user2')
        self.driver2.find_element(By.TAG_NAME, 'button').click()

        # Wait for user 2 to join from user 1's perspective
        WebDriverWait(self.driver1, 10).until(EC.text_to_be_present_in_element((By.ID, 'messages'), 'user2 joined.'))
        initial_messages_user1 = self.driver1.find_element(By.ID, 'messages').text

        # User 3 attempts to join
        self.driver3.get('http://localhost:5000')
        self.driver3.find_element(By.ID, 'username').send_keys('user3')
        self.driver3.find_element(By.TAG_NAME, 'button').click()

        # Check that User 3 sees the "Room full" message
        # This message is sent directly to the user, so it might not be in the chat log.
        # A better check is that user1's log does NOT contain user3.
        time.sleep(2) # Give time for any incorrect messages to appear
        final_messages_user1 = self.driver1.find_element(By.ID, 'messages').text
        self.assertNotIn('user3', final_messages_user1)
        self.assertEqual(initial_messages_user1, final_messages_user1)

    def test_message_send_before_secure_connection(self):
        # User 1 joins
        self.driver1.get('http://localhost:5000')
        self.driver1.find_element(By.ID, 'username').send_keys('user1')
        self.driver1.find_element(By.TAG_NAME, 'button').click()

        # User 1 tries to send a message before User 2 joins
        self.driver1.find_element(By.ID, 'messageInput').send_keys('Early message')
        self.driver1.find_element(By.XPATH, "//button[text()='Send']").click()

        # Check for "Cannot send message"
        wait = WebDriverWait(self.driver1, 10)
        wait.until(EC.text_to_be_present_in_element((By.ID, 'messages'), 'Cannot send message: secure connection not yet established.'))
        messages = self.driver1.find_element(By.ID, 'messages').text
        self.assertIn('Cannot send message', messages)

if __name__ == '__main__':
    unittest.main()
