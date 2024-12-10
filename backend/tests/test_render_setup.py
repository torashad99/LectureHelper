from pathlib import Path
import os
import shutil
import subprocess

# Set up test environment
render_dir = Path('/opt/render/project/src')
if render_dir.exists():
    shutil.rmtree(render_dir)
render_dir.mkdir(parents=True, exist_ok=True)

# Set environment variables (matching render.yaml)
os.environ.update({
    'PYTHONPATH': '/opt/render/project/src',
    'DATA_DIR': '/opt/render/project/src/data/embeddings',
    'VTT_DIRECTORY': '/opt/render/project/src/data/CS410Transcripts/vtt',
    'TXT_DIRECTORY': '/opt/render/project/src/data/CS410Transcripts/txt',
    'RENDER_PROJECT_DIR': '/opt/render/project/src'
})

# Simulate build command
build_steps = [
    'python -m pip install --upgrade pip',
    'pip install -r requirements.txt',
    'mkdir -p /opt/render/project/src/data/embeddings',
    'mkdir -p /opt/render/project/src/data/CS410Transcripts/vtt',
    'cp -rv backend/* /opt/render/project/src/',
    'cp -rv CS410Transcripts/vtt/* /opt/render/project/src/data/CS410Transcripts/vtt/',
    'cp -rv data/embeddings/* /opt/render/project/src/data/embeddings/',
    'python -c "from app import create_app; app=create_app()"'
]

for step in build_steps:
    print(f"\nExecuting: {step}")
    result = subprocess.run(step, shell=True, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    if result.returncode != 0:
        print(f"Step failed with code {result.returncode}")
        break