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
        
        # Create base directories
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create data directories
        data_dir = self.project_dir / 'data'
        embeddings_dir = data_dir / 'embeddings'
        vtt_dir = data_dir / 'CS410Transcripts' / 'vtt'
        txt_dir = data_dir / 'CS410Transcripts' / 'txt'
        
        for dir_path in [embeddings_dir, vtt_dir, txt_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ.update({
            'PYTHONPATH': str(self.project_dir),
            'RENDER_PROJECT_DIR': str(self.project_dir),
            'DATA_DIR': str(embeddings_dir),
            'VTT_DIRECTORY': str(vtt_dir),
            'TXT_DIRECTORY': str(txt_dir)
        })
        
        # Copy necessary files
        source_dir = Path.cwd()
        for item in ['app.py', 'config.py', 'routes', 'services']:
            if (source_dir / item).is_file():
                shutil.copy2(source_dir / item, self.project_dir)
            elif (source_dir / item).is_dir():
                shutil.copytree(source_dir / item, self.project_dir / item, dirs_exist_ok=True)
        
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