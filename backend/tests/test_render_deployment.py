import unittest
from pathlib import Path
import shutil
import os
import subprocess

class TestRenderDeployment(unittest.TestCase):
    def setUp(self):
        # Simulate Render's directory structure
        self.render_dir = Path('/opt/render/project/src')
        self.test_dir = Path.cwd() / 'test_render'
        self.project_dir = self.test_dir / 'opt' / 'render' / 'project' / 'src'
        
        # Create directories
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ['PYTHONPATH'] = str(self.project_dir)
        
    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            
    def test_build_process(self):
        # Test directory creation
        data_dir = self.project_dir / 'data'
        embeddings_dir = data_dir / 'embeddings'
        vtt_dir = data_dir / 'CS410Transcripts' / 'vtt'
        
        os.makedirs(embeddings_dir, exist_ok=True)
        os.makedirs(vtt_dir, exist_ok=True)
        
        # Test file copying - removed 'backend/' prefix since we're already in backend directory
        backend_files = ['app.py', 'config.py']
        for file in backend_files:
            shutil.copy2(file, self.project_dir)
            
        # Verify directory structure
        self.assertTrue(embeddings_dir.exists())
        self.assertTrue(vtt_dir.exists())
        
        # Verify Python environment
        try:
            subprocess.run(['python3', '-c', 'import flask'], check=True)
        except subprocess.CalledProcessError:
            self.fail("Flask not installed properly")
            
    def test_environment_variables(self):
        required_vars = ['PYTHONPATH', 'OPEN_AI_API_KEY']
        for var in required_vars:
            self.assertIsNotNone(os.getenv(var), f"Missing environment variable: {var}") 