import unittest
from pathlib import Path
import os
import json
from dotenv import load_dotenv

class TestDeploymentSetup(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.base_dir = Path.cwd()
        # Create test directories
        self.data_dir = self.base_dir / 'test_data'
        self.embeddings_dir = self.data_dir / 'embeddings'
        self.vtt_dir = self.data_dir / 'CS410Transcripts' / 'vtt'
        
        # Create directories
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        self.vtt_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files
        self.create_test_files()
        
    def create_test_files(self):
        # Create test VTT file
        test_vtt = self.vtt_dir / 'L1.vtt'
        test_vtt.write_text("WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nTest content")
        
        # Create test embeddings file
        test_embedding = {
            "text": "test chunk",
            "embedding": [0.1] * 10,
            "timestamp": "00:00:00.000",
            "video_id": "L1"
        }
        test_embeddings = self.embeddings_dir / 'combined_embeddings.jsonl'
        test_embeddings.write_text(json.dumps(test_embedding))
        
    def tearDown(self):
        # Clean up test directories
        import shutil
        if self.data_dir.exists():
            shutil.rmtree(self.data_dir)
        
    def test_environment_variables(self):
        self.assertIsNotNone(os.getenv('OPEN_AI_API_KEY'), "OPEN_AI_API_KEY not set")
        
    def test_directory_structure(self):
        dirs = [self.data_dir, self.embeddings_dir, self.vtt_dir]
        for dir_path in dirs:
            self.assertTrue(dir_path.exists(), f"Directory missing: {dir_path}")
            
    def test_vtt_files(self):
        vtt_files = list(self.vtt_dir.glob('L*.vtt'))
        self.assertTrue(len(vtt_files) > 0, "No VTT files found")
        
    def test_embeddings_file(self):
        embeddings_file = self.embeddings_dir / 'combined_embeddings.jsonl'
        self.assertTrue(embeddings_file.exists(), "Embeddings file missing")