import unittest
from unittest.mock import patch
from services.embedding_service import client
import os

class TestOpenAIClient(unittest.TestCase):
    def setUp(self):
        os.environ['OPEN_AI_API_KEY'] = 'test_key'

    def test_client_initialization(self):
        with patch('openai.OpenAI') as mock_openai:
            from services.embedding_service import client
            mock_openai.assert_called_once_with(
                api_key='test_key',
                base_url="https://api.openai.com/v1",
                timeout=60,
                max_retries=3
            )

if __name__ == '__main__':
    unittest.main() 