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

def process_query(query):
    print("\n=== Starting Search Process ===")
    embeddings_file = Path.cwd() / 'data' / 'embeddings' / 'embeddings.jsonl'
    
    with open(embeddings_file, 'r') as f:
        lines = f.readlines()
        embeddings = {}
        for line in lines:
            line = json.loads(line)
            embeddings[line['text']] = line['embedding']
    
    query_embedding = get_embedding(query)
    best_chunk = None
    best_score = float("-inf")
    
    for chunk, embedding in embeddings.items():
        score = np.dot(embedding, query_embedding)
        if score > best_score:
            best_chunk = chunk
            best_score = score
    
    if not best_chunk:
        return []
        
    system_prompt = "You are a friendly and supportive teaching assistant for a course on Text Information Systems."
    prompt = f"Answer the question using the following information:\n\n{best_chunk}\n\nQuestion: {query}"
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4"
    )
    
    response_text = chat_completion.choices[0].message.content
    vtt_directory = Path.cwd() / 'CS410Transcripts' / 'vtt'
    lecture_index, start_time = sliding_window_vtt(best_chunk, vtt_directory)
    
    if lecture_index and start_time:
        lecture_number = int(lecture_index[1:])
        return [{
            "response": response_text,
            "lecture": lecture_number,
            "timestamp": start_time,
            "score": float(best_score)
        }]
    
    return []