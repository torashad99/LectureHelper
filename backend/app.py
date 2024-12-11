from flask import Flask, jsonify, make_response
from flask_cors import CORS
from routes.api import api_routes
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

def create_app():
    load_dotenv()
    
    # Initialize OpenAI client globally
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        client = None

    app = Flask(__name__)
    CORS(app)
    
    app.register_blueprint(api_routes, url_prefix='/api')
    
    @app.route('/api/health')
    def health_check():
        try:
            status = check_directories()
            is_healthy = (
                status["directories"]["data_dir"]["exists"] and
                status["directories"]["vtt_dir"]["exists"] and
                status["files"]["embeddings"]["exists"] and
                len(status["directories"]["vtt_dir"]["vtt_files"]) > 0
            )
            
            response = make_response(
                jsonify({
                    "status": "healthy" if is_healthy else "unhealthy",
                    "details": status
                })
            )
            response.headers['Content-Type'] = 'application/json'
            return response, 200 if is_healthy else 503
            
        except Exception as e:
            return make_response(
                jsonify({
                    "status": "error",
                    "error": str(e)
                }),
                500,
                {'Content-Type': 'application/json'}
            )
    
    return app

def debug_directory_contents():
    # Check if we're in production (Render) or local environment
    if os.environ.get('RENDER'):
        base_dir = Path('/opt/render/project/src')
    else:
        base_dir = Path.cwd().parent  # Go up one level to LectureHelper/
    
    data_dir = Path(os.environ.get('DATA_DIR', base_dir / 'backend' / 'data' / 'embeddings'))
    vtt_dir = Path(os.environ.get('VTT_DIRECTORY', base_dir / 'CS410Transcripts' / 'vtt')).resolve()
    
    print("\n=== Directory Content Debug ===")
    print(f"\nCurrent Working Directory: {Path.cwd()}")
    print(f"Parent Directory: {Path.cwd().parent}")
    
    print(f"\nBase Directory: {base_dir}")
    print("Contents:", [str(p) for p in base_dir.glob('*')])
    
    print(f"\nData Directory: {data_dir}")
    if data_dir.exists():
        print("Contents:", [str(p) for p in data_dir.glob('*')])
        embeddings_file = data_dir / 'embeddings.jsonl'
        if embeddings_file.exists():
            print(f"Embeddings file size: {embeddings_file.stat().st_size} bytes")
    else:
        print("Directory does not exist")
    
    print(f"\nVTT Directory: {vtt_dir}")
    if vtt_dir.exists():
        print("All files:", [str(p) for p in vtt_dir.glob('*')])
        print("VTT files:", [str(p) for p in vtt_dir.glob('L*.vtt')])
        if vtt_dir.is_dir():
            print("\nDetailed VTT directory listing:")
            for item in vtt_dir.iterdir():
                print(f"- {item.name} ({'directory' if item.is_dir() else 'file'})")
    else:
        print("Directory does not exist")
    print("\n===========================")

def check_directories():
    # Check if we're in production (Render) or local environment
    if os.environ.get('RENDER'):
        base_dir = Path('/opt/render/project/src')
    else:
        # Get absolute path to LectureHelper directory
        current_dir = Path.cwd()
        if 'LectureHelper' not in str(current_dir):
            raise RuntimeError("Must be run from within LectureHelper project")
        base_dir = current_dir.parent if current_dir.name == 'backend' else current_dir
    
    # Use environment variables with local fallbacks
    data_dir = Path(os.environ.get('DATA_DIR', base_dir / 'backend' / 'data' / 'embeddings'))
    vtt_dir = Path(os.environ.get('VTT_DIRECTORY', base_dir / 'backend' / 'CS410Transcripts' / 'vtt')).resolve()
    
    print(f"\nChecking directories:")
    print(f"Base dir: {base_dir}")
    print(f"VTT dir: {vtt_dir}")
    print(f"VTT files: {list(vtt_dir.glob('L*.vtt'))}")
    
    # Create directories if they don't exist (for local development)
    if not os.environ.get('RENDER'):
        data_dir.mkdir(parents=True, exist_ok=True)
        vtt_dir.mkdir(parents=True, exist_ok=True)
    
    status = {
        "directories": {
            "data_dir": {
                "path": str(data_dir),
                "exists": data_dir.exists(),
                "is_directory": data_dir.is_dir() if data_dir.exists() else False
            },
            "vtt_dir": {
                "path": str(vtt_dir),
                "exists": vtt_dir.exists(),
                "is_directory": vtt_dir.is_dir() if vtt_dir.exists() else False,
                "vtt_files": [f.name for f in vtt_dir.glob('L*.vtt')] if vtt_dir.exists() else []
            }
        },
        "files": {
            "embeddings": {
                "path": str(data_dir / 'embeddings.jsonl'),
                "exists": (data_dir / 'embeddings.jsonl').exists()
            }
        }
    }
    return status

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)