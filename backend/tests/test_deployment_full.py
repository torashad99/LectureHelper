import unittest
from pathlib import Path
import os
import shutil
import subprocess
import sys
import json

class TestDeploymentFull(unittest.TestCase):
    def setUp(self):
        # Reference the test setup from test_render_deployment.py
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
            
        # Copy embeddings file
        source_embeddings = Path.cwd() / 'data' / 'embeddings' / 'embeddings.jsonl'
        if source_embeddings.exists():
            shutil.copy2(source_embeddings, embeddings_dir / 'embeddings.jsonl')
        
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
        
        # First, create the config package
        config_dir = self.project_dir / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py to make it a package
        (config_dir / '__init__.py').touch()
        
        # Copy config files
        if (source_dir / 'config').is_dir():
            for config_file in (source_dir / 'config').glob('*.py'):
                shutil.copy2(config_file, config_dir)
        
        # Copy other files
        for item in ['app.py', 'routes', 'services']:
            if (source_dir / item).is_file():
                shutil.copy2(source_dir / item, self.project_dir)
            elif (source_dir / item).is_dir():
                shutil.copytree(source_dir / item, self.project_dir / item, dirs_exist_ok=True)

    def test_gunicorn_config(self):
        gunicorn_path = shutil.which('gunicorn')
        if not gunicorn_path:
            self.skipTest("Gunicorn not found")
            
        os.chdir(self.project_dir)
        cmd = [gunicorn_path, '--check-config', 'app:create_app()']
        result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
        self.assertEqual(result.returncode, 0, f"Gunicorn config check failed: {result.stderr}")

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main(verbosity=2) 