import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import re
import numpy as np
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def sliding_window_vtt(best_chunk, vtt_directory):
    # Normalize the search text
    words = best_chunk.split()
    start_index = 1
    window_size = 5
    
    # Ensure vtt_directory is a Path object
    vtt_dir = Path(vtt_directory)
    
    # Debug logging
    print(f"Searching in VTT directory: {vtt_dir}")
    print(f"Available VTT files: {list(vtt_dir.glob('L*.vtt'))}")
    
    for i in range(start_index, len(words) - window_size + 1):
        window = ' '.join(words[i:i+window_size])
        
        # Search through all lecture VTT files
        for vtt_file in vtt_dir.glob('L*.vtt'):
            try:
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
                            print(f"Found match in {lecture_index} at {timestamp}")
                            return lecture_index, timestamp
                            
            except Exception as e:
                print(f"Error processing {vtt_file}: {e}")
                continue
    
    print("No matches found in any VTT files")
    return None, None

def process_lecture_query(query):
    print("\n=== Starting Search Process ===")
    
    # Use environment variables for paths
    base_dir = Path('/opt/render/project/src')
    embeddings_dir = Path(os.environ.get('DATA_DIR', base_dir / 'data' / 'embeddings'))
    vtt_dir = Path(os.environ.get('VTT_DIRECTORY', base_dir / 'data' / 'CS410Transcripts' / 'vtt'))
    embeddings_file = embeddings_dir / 'embeddings.jsonl'
    
    print(f"Looking for embeddings file at: {embeddings_file}")
    print(f"VTT directory at: {vtt_dir}")
    
    if not embeddings_file.exists():
        print(f"Embeddings file not found at {embeddings_file}")
        return []
    
    query_embedding = get_embedding(query)
    matches = []
    
    with open(embeddings_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            score = np.dot(data['embedding'], query_embedding)
            if score > 0.5:  # Keep only relevant matches
                matches.append({
                    "text": data['text'],
                    "score": float(score)
                })
    
    # Sort by score
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    system_prompt = "You are a friendly and supportive teaching assistant for a course on Text Information Systems."
    
    # Process top matches
    results = []
    for match in matches[:5]:
        lecture_index, timestamp = sliding_window_vtt(match['text'], str(vtt_dir))
        if lecture_index and timestamp:
            prompt = f"Answer the question using the following information:\n\n{match['text']}\n\nQuestion: {query}"
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model="gpt-4"
                )
                
                results.append({
                    "lecture": lecture_index,
                    "response": chat_completion.choices[0].message.content,
                    "timestamp": timestamp,
                    "score": match['score']
                })
            except Exception as e:
                print(f"OpenAI API error: {e}")
                continue
    
    return results