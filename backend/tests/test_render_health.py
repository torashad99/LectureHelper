import unittest
from pathlib import Path
import os
import requests
from app import create_app
import threading
import time

class TestRenderHealth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start Flask app in a separate thread
        cls.app = create_app()
        cls.thread = threading.Thread(target=cls.app.run, kwargs={'port': 10999})
        cls.thread.daemon = True
        cls.thread.start()
        time.sleep(1)  # Wait for server to start
        
    def test_health_endpoint(self):
        try:
            response = requests.get('http://localhost:10999/api/health')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['status'], 'healthy')
        except requests.RequestException as e:
            self.fail(f"Health check failed: {str(e)}") 