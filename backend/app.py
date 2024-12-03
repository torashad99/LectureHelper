from flask import Flask, jsonify
from flask_cors import CORS
from routes.video_routes import video_routes
from routes.api import api_routes
from services.embedding_service import initialize_embeddings

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register blueprints
app.register_blueprint(video_routes)
app.register_blueprint(api_routes, url_prefix='/api')

# Initialize embeddings when the app starts
initialize_embeddings()

if __name__ == '__main__':
    app.run(debug=True)