from flask import Blueprint, request, jsonify
from services.embedding_service import process_lecture_query

api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/search', methods=['GET'])
def search():
    try:
        query = request.args.get('q')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Missing query'
            }), 400
            
        matches = process_lecture_query(query)
        
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

