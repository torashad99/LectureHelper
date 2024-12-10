from flask import Blueprint, request, jsonify, make_response
from config.video_config import VIDEO_MAPPINGS, VIDEO_TITLES

video_routes = Blueprint('video_routes', __name__)

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

