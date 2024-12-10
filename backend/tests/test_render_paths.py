import unittest
from pathlib import Path
import shutil
import os

class TestRenderPaths(unittest.TestCase):
    def setUp(self):
        # Use a test directory instead of /opt/render
        self.test_dir = Path.cwd() / 'test_render'
        self.render_dir = self.test_dir / 'project' / 'src'
        self.render_dir.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        # Clean up test directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        
    def test_render_file_copy(self):
        try:
            # Create test directories
            os.makedirs(self.render_dir / 'data' / 'embeddings', exist_ok=True)
            os.makedirs(self.render_dir / 'data' / 'CS410Transcripts' / 'vtt', exist_ok=True)
            
            # Create test files
            (self.render_dir / 'app.py').touch()
            (self.render_dir / 'data' / 'embeddings' / 'test.jsonl').touch()
            (self.render_dir / 'data' / 'CS410Transcripts' / 'vtt' / 'L1.vtt').touch()
            
            # Verify paths
            self.assertTrue((self.render_dir / 'app.py').exists())
            self.assertTrue((self.render_dir / 'data' / 'embeddings').exists())
            self.assertTrue((self.render_dir / 'data' / 'CS410Transcripts' / 'vtt').exists())
            
        except Exception as e:
            self.fail(f"Test failed: {str(e)}")