from flask import Flask
from flask_cors import CORS
from routes.api import api_routes
from openai import OpenAI
from dotenv import load_dotenv
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)