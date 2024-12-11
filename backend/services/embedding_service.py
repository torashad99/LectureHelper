import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import re
import numpy as np

load_dotenv()

client = OpenAI(api_key=os.environ["OPEN_AI_API_KEY"])

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def sliding_window_vtt(best_chunk, vtt_directory):
    # Following example from examples/embeddings/openai/04_reverse_search.py
    words = best_chunk.split()
    start_index = 1
    window_size = 5
    
    for i in range(start_index, len(words) - window_size + 1):
        window = ' '.join(words[i:i+window_size])
        
        for vtt_file in Path(vtt_directory).glob('L*.vtt'):
            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                pattern = re.compile(re.escape(window), re.IGNORECASE)
                match = pattern.search(content)
                
                if match:
                    lines = content[:match.start()].split('\n')
                    timestamp = None
                    
                    for line in reversed(lines):
                        if '-->' in line:
                            timestamp = line.split(' --> ')[0]
                            break
                    
                    if timestamp:
                        lecture_index = vtt_file.stem
                        return lecture_index, timestamp
    
    return None, None

def process_multiple_videos_query(query, video_ids):
    print("\n=== Starting Search Process ===")
    base_dir = Path(os.environ.get('RENDER_PROJECT_DIR', Path.cwd()))
    embeddings_dir = Path(os.environ.get('DATA_DIR', base_dir / 'data' / 'embeddings'))
    embeddings_file = embeddings_dir / 'embeddings.jsonl'
    
    if not embeddings_file.exists():
        print(f"Embeddings file not found at {embeddings_file}")
        return []
    
    query_embedding = get_embedding(query)
    matches = []
    
    # Load embeddings and find matches
    with open(embeddings_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            score = np.dot(data['embedding'], query_embedding)
            if score > 0.5:
                matches.append({
                    "text": data['text'],
                    "score": float(score)
                })
    
    # Sort by score
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Process top matches to find timestamps
    results = []
    vtt_dir = Path.cwd() / 'CS410Transcripts' / 'vtt'
    
    for match in matches[:5]:
        lecture_index, timestamp = sliding_window_vtt(match['text'], str(vtt_dir))
        if lecture_index and timestamp and lecture_index in video_ids:
            results.append({
                "video_id": lecture_index,
                "response": match['text'],
                "timestamp": timestamp,
                "score": match['score']
            })
    
    return results