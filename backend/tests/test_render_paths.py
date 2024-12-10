import unittest
import os
from pathlib import Path
import shutil

class TestRenderPaths(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path('test_render')
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        
        # Create the directory structure
        self.project_dir = self.test_dir / 'opt' / 'render' / 'project' / 'src'
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy backend files - using current directory as source
        source_dir = Path.cwd()
        for item in ['app.py', 'config.py', 'routes', 'services']:
            if (source_dir / item).is_file():
                shutil.copy2(source_dir / item, self.project_dir)
            elif (source_dir / item).is_dir():
                shutil.copytree(source_dir / item, self.project_dir / item, dirs_exist_ok=True)
        
        # Create data directories
        (self.project_dir / 'data' / 'embeddings').mkdir(parents=True, exist_ok=True)
        (self.project_dir / 'data' / 'CS410Transcripts' / 'vtt').mkdir(parents=True, exist_ok=True)
        (self.project_dir / 'data' / 'CS410Transcripts' / 'txt').mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ.update({
            'PYTHONPATH': str(self.project_dir),
            'RENDER_PROJECT_DIR': str(self.project_dir),
            'DATA_DIR': str(self.project_dir / 'data' / 'embeddings'),
            'VTT_DIRECTORY': str(self.project_dir / 'data' / 'CS410Transcripts' / 'vtt'),
            'TXT_DIRECTORY': str(self.project_dir / 'data' / 'CS410Transcripts' / 'txt')
        })
        
    def test_directory_structure(self):
        # Change to project directory (not backend)
        os.chdir(self.project_dir)
        
        # Import and run app creation
        from app import create_app
        app = create_app()
        
        # Verify directories exist
        self.assertTrue((self.project_dir / 'data' / 'embeddings').exists())
        self.assertTrue((self.project_dir / 'data' / 'CS410Transcripts' / 'vtt').exists())
        self.assertTrue((self.project_dir / 'data' / 'CS410Transcripts' / 'txt').exists())
        
    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)