import unittest
from app import app

class TestVideoAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_video_url(self):
        # Test valid lecture number
        response = self.app.get('/api/video/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json)
        
        # Test invalid lecture number
        response = self.app.get('/api/video/999')
        self.assertEqual(response.status_code, 404)

    def test_video_url_format(self):
        response = self.app.get('/api/video/1')
        url = response.json['url']
        self.assertTrue(url.startswith('https://www.youtube.com/watch?v=')) 