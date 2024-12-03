from flask import Blueprint, request, jsonify
from services.embedding_service import process_all_videos

api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/process-embeddings', methods=['POST'])
def process_embeddings():
    data = request.get_json()
    video_ids = data.get('video_ids', [])
    
    if not video_ids:
        return jsonify({'error': 'No video IDs provided'}), 400
        
    try:
        process_all_videos(video_ids)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 