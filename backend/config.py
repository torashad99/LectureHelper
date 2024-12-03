import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')
    VTT_DIRECTORY = os.getenv('VTT_DIRECTORY', 'CS410Transcripts/vtt')
    EMBEDDINGS_FILE = os.getenv('EMBEDDINGS_FILE', 'embeddings.jsonl') 