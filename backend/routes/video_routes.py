from flask import Blueprint, request, jsonify, make_response
from services.video_processor import VideoProcessor
from config.video_config import VIDEO_MAPPINGS, VIDEO_TITLES
from pathlib import Path
import shutil
import json
from services.embedding_service import process_transcript, process_user_query, process_multiple_videos_query, init_lecture_embeddings

video_routes = Blueprint('video_routes', __name__)
video_processor = VideoProcessor()

@video_routes.route('/api/videos', methods=['GET'])
def get_all_videos():
    try:
        videos = [
            {"id": id, "url": url, "title": VIDEO_TITLES.get(id, '')}
            for id, url in VIDEO_MAPPINGS.items()
        ]
        response = make_response(jsonify({"videos": videos}))
        response.headers['Content-Type'] = 'application/json'
        return response
    except Exception as e:
        return make_response(
            jsonify({"error": str(e)}),
            500,
            {'Content-Type': 'application/json'}
        )

@video_routes.route('/api/videos/upload', methods=['POST'])
def upload_video():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return make_response(
                jsonify({
                    'success': False,
                    'error': 'No URL provided'
                }),
                400
            )

        video_data = video_processor.process_video(data['url'])
        video_id = video_data['id']  # Use YouTube video ID instead of incremental number
        
        VIDEO_MAPPINGS[video_id] = data['url']
        VIDEO_TITLES[video_id] = video_data['title']
        
        return make_response(
            jsonify({
                'success': True,
                'video': {
                    'id': video_id,
                    'url': data['url'],
                    'title': video_data['title']
                }
            }),
            200
        )
    except ValueError as ve:
        return make_response(
            jsonify({
                'success': False,
                'error': str(ve)
            }),
            400
        )
    except Exception as e:
        return make_response(
            jsonify({
                'success': False,
                'error': str(e)
            }),
            500
        )

@video_routes.route('/api/video/<int:lecture_number>', methods=['GET'])
def get_video_url(lecture_number):
    url = VIDEO_MAPPINGS.get(lecture_number)
    if url:
        return jsonify({"url": url})
    return jsonify({"error": "Video not found"}), 404 

@video_routes.route('/api/videos/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    try:
        video_dir = Path.cwd() / 'data' / 'user_videos' / video_id
        
        if not video_dir.exists():
            return jsonify({'error': 'Video not found'}), 404
            
        # Remove directory and all contents
        shutil.rmtree(video_dir)
        
        # Remove from mappings
        if video_id in VIDEO_MAPPINGS:
            del VIDEO_MAPPINGS[video_id]
        if video_id in VIDEO_TITLES:
            del VIDEO_TITLES[video_id]
            
        return jsonify({'success': True}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@video_routes.route('/api/videos/init', methods=['GET'])
def init_videos():
    try:
        # Scan the user_videos directory
        videos_dir = Path.cwd() / 'data' / 'user_videos'
        videos = []
        
        if videos_dir.exists():
            for video_dir in videos_dir.iterdir():
                if video_dir.is_dir():
                    metadata_file = video_dir / 'metadata.json'
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            video_id = metadata['id']
                            VIDEO_MAPPINGS[video_id] = metadata['url']
                            VIDEO_TITLES[video_id] = metadata['title']
                            videos.append({
                                'id': video_id,
                                'url': metadata['url'],
                                'title': metadata['title']
                            })
        
        return jsonify({'videos': videos}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@video_routes.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    video_ids = request.args.getlist('video_ids[]')  # Handle multiple video IDs
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Missing query parameter'
        }), 400
        
    if not video_ids:
        return jsonify({
            'success': False,
            'error': 'Missing video_ids parameter'
        }), 400
    
    try:
        results = process_multiple_videos_query(query, video_ids)
        
        # Add titles to results
        for result in results:
            result['title'] = VIDEO_TITLES.get(result['video_id'], '')
            
        return jsonify({
            'success': True,
            'results': results
        }), 200
            
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

