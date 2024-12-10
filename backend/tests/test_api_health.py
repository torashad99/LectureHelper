import unittest
import sys
from pathlib import Path
import json
import os

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from app import create_app

class TestAPIHealth(unittest.TestCase):
    def setUp(self):
        # Set up test environment variables
        os.environ['OPEN_AI_API_KEY'] = 'test_key'
        os.environ['VTT_DIRECTORY'] = str(Path.cwd() / 'test_data' / 'CS410Transcripts' / 'vtt')
        os.environ['EMBEDDINGS_FILE'] = str(Path.cwd() / 'test_data' / 'embeddings' / 'embeddings.jsonl')
        os.environ['TXT_DIRECTORY'] = str(Path.cwd() / 'test_data' / 'CS410Transcripts' / 'txt')
        
        # Create test directories
        self.test_dir = Path.cwd() / 'test_data'
        self.embeddings_dir = self.test_dir / 'embeddings'
        self.vtt_dir = self.test_dir / 'CS410Transcripts' / 'vtt'
        self.txt_dir = self.test_dir / 'CS410Transcripts' / 'txt'
        
        # Create directories and test files
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        self.vtt_dir.mkdir(parents=True, exist_ok=True)
        self.txt_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test VTT and TXT files for L1 through L4
        for i in range(1, 5):
            (self.vtt_dir / f'L{i}.vtt').write_text(f"WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nTest content {i}")
            (self.txt_dir / f'L{i}.txt').write_text(f"Test content {i}")
        
        # Create an empty embeddings file
        (self.embeddings_dir / 'embeddings.jsonl').write_text('')
        
        self.app = create_app()
        self.client = self.app.test_client()
        self.client.testing = True

    def tearDown(self):
        # Clean up test directories
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_health_check(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_embeddings_initialization(self):
        embeddings_file = self.embeddings_dir / 'embeddings.jsonl'
        self.assertTrue(embeddings_file.exists())

if __name__ == '__main__':
    unittest.main()