import unittest
from pathlib import Path
import os
import shutil
import subprocess
import json
from dotenv import load_dotenv
import sys

class TestFullDeployment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Install required packages
        subprocess.run([sys.executable, "-m", "pip", "install", "gunicorn"], check=True)
    
    def setUp(self):
        # Create test environment structure
        self.test_dir = Path.cwd() / 'test_render'
        self.project_dir = self.test_dir / 'opt' / 'render' / 'project' / 'src'
        self.data_dir = self.project_dir / 'data'
        self.embeddings_dir = self.data_dir / 'embeddings'
        self.vtt_dir = self.data_dir / 'CS410Transcripts' / 'vtt'
        self.txt_dir = self.data_dir / 'CS410Transcripts' / 'txt'
        
        # Create all directories
        for dir_path in [self.embeddings_dir, self.vtt_dir, self.txt_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Set environment variables
        os.environ.update({
            'PYTHONPATH': str(self.project_dir),
            'RENDER_PROJECT_DIR': str(self.project_dir),
            'DATA_DIR': str(self.embeddings_dir),
            'VTT_DIRECTORY': str(self.vtt_dir),
            'TXT_DIRECTORY': str(self.txt_dir),
            'OPEN_AI_API_KEY': 'test_key'
        })
        
        # Create test data
        self._create_test_data()
        
    def _create_test_data(self):
        # Create test VTT files
        for i in range(1, 5):
            vtt_content = f"""WEBVTT

00:00:00.000 --> 00:00:05.000
Test content for lecture {i}"""
            (self.vtt_dir / f'L{i}.vtt').write_text(vtt_content)
            
            # Create corresponding TXT files
            (self.txt_dir / f'L{i}.txt').write_text(f"Test content for lecture {i}")
            
    def test_1_directory_structure(self):
        """Test that all required directories exist"""
        for dir_path in [self.embeddings_dir, self.vtt_dir, self.txt_dir]:
            self.assertTrue(dir_path.exists(), f"Directory missing: {dir_path}")
            
    def test_2_file_copying(self):
        """Test copying files from backend to project directory"""
        source_dir = Path.cwd()
        for item in ['app.py', 'config.py', 'routes', 'services']:
            if (source_dir / item).is_file():
                shutil.copy2(source_dir / item, self.project_dir)
            elif (source_dir / item).is_dir():
                shutil.copytree(source_dir / item, self.project_dir / item, dirs_exist_ok=True)
                
        self.assertTrue((self.project_dir / 'app.py').exists())
        
    def test_3_app_creation(self):
        """Test that the Flask app can be created"""
        cmd = f"PYTHONPATH={self.project_dir} {sys.executable} -c 'from app import create_app; app=create_app()'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"App creation failed: {result.stderr}")
        
    def test_4_gunicorn_startup(self):
        """Test that gunicorn can start the app"""
        gunicorn_path = shutil.which('gunicorn')
        if not gunicorn_path:
            self.skipTest("Gunicorn not installed")
            
        cmd = f"PYTHONPATH={self.project_dir} {gunicorn_path} --check-config 'app:create_app()'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Gunicorn config check failed: {result.stderr}")

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main(verbosity=2) 