from flask import Blueprint, request, jsonify
from services.embedding_service import process_multiple_videos_query

api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/search', methods=['GET'])
def search():
    try:
        query = request.args.get('q')
        video_ids = request.args.getlist('video_ids[]')
        
        if not query or not video_ids:
            return jsonify({
                'success': False,
                'error': 'Missing query or video IDs'
            }), 400
            
        matches = process_multiple_videos_query(query, video_ids)
        
        return jsonify({
            'success': True,
            'results': matches
        })
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

