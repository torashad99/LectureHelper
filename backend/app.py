from flask import Flask, jsonify
from routes.video_routes import video_routes
from routes.api import api_routes
from services.embedding_service import init_lecture_embeddings
from pathlib import Path
import shutil
import os

def setup_directories():
    # Create required directories
    base_dir = Path.cwd()
    data_dir = base_dir / 'data' / 'embeddings'
    transcript_dir = base_dir / 'CS410Transcripts' / 'txt'
    vtt_dir = base_dir / 'CS410Transcripts' / 'vtt'
    
    data_dir.mkdir(parents=True, exist_ok=True)
    transcript_dir.mkdir(parents=True, exist_ok=True)
    vtt_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if transcript files exist
    if not any(transcript_dir.glob('L*.txt')):
        print("Error: No lecture transcripts found in CS410Transcripts/txt")
        print("Please ensure L1.txt through L4.txt exist in the directory")
        return False
        
    if not any(vtt_dir.glob('L*.vtt')):
        print("Error: No VTT files found in CS410Transcripts/vtt")
        print("Please ensure L1.vtt through L4.vtt exist in the directory")
        return False
    
    return True

def create_app():
    app = Flask(__name__)
    
    # Setup required directories and check files
    if not setup_directories():
        print("Failed to initialize required directories and files")
        exit(1)
    
    # Initialize embeddings before registering routes
    print("Initializing lecture embeddings...")
    init_lecture_embeddings()
    
    # Register blueprints
    app.register_blueprint(video_routes)
    app.register_blueprint(api_routes)
    
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)