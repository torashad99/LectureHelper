from flask import Flask, jsonify
from routes.video_routes import video_routes
from routes.api import api_routes
from services.embedding_service import init_lecture_embeddings
from pathlib import Path
import shutil
import os

def setup_directories():
    # Use environment variables for paths
    base_dir = Path(os.environ.get('RENDER_PROJECT_DIR', Path.cwd()))
    data_dir = Path(os.environ.get('DATA_DIR', base_dir / 'data' / 'embeddings'))
    transcript_dir = Path(os.environ.get('TXT_DIRECTORY', base_dir / 'CS410Transcripts' / 'txt'))
    vtt_dir = Path(os.environ.get('VTT_DIRECTORY', base_dir / 'CS410Transcripts' / 'vtt'))
    
    for directory in [data_dir, transcript_dir, vtt_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        
    # Add logging for debugging
    print(f"Checking directories:")
    print(f"Data dir: {data_dir} - exists: {data_dir.exists()}")
    print(f"Transcript dir: {transcript_dir} - exists: {transcript_dir.exists()}")
    print(f"VTT dir: {vtt_dir} - exists: {vtt_dir.exists()}")
    
    return all(d.exists() for d in [data_dir, transcript_dir, vtt_dir])

def create_app():
    try:
        app = Flask(__name__)
        
        # Setup required directories and check files
        if not setup_directories():
            print("Failed to initialize required directories and files")
            raise RuntimeError("Directory setup failed")
        
        print("Directories initialized successfully")
        
        # Initialize embeddings before registering routes
        print("Initializing lecture embeddings...")
        init_lecture_embeddings()
        print("Embeddings initialized successfully")
        
        # Register blueprints
        app.register_blueprint(video_routes)
        app.register_blueprint(api_routes)
        
        @app.route('/api/health')
        def health_check():
            return jsonify({"status": "healthy"}), 200
        
        return app
    except Exception as e:
        print(f"Application initialization failed: {str(e)}")
        raise

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)