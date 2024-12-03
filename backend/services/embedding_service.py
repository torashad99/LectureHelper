import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import re
import numpy as np

load_dotenv()

client = OpenAI(api_key=os.environ["OPEN_AI_API_KEY"])

def sliding_window_vtt(best_chunk, vtt_directory):
    # Split the best chunk into words
    words = best_chunk.split()
    start_index = 1
    window_size = 5
    
    for i in range(start_index, len(words) - window_size + 1):
        window = ' '.join(words[i:i+window_size])
        
        vtt_file = Path(vtt_directory) / 'transcript.vtt'
        if vtt_file.exists():
            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                pattern = re.compile(re.escape(window), re.IGNORECASE)
                match = pattern.search(content)
                
                if match:
                    lines = content[:match.start()].split('\n')
                    for line in reversed(lines):
                        if '-->' in line:
                            return line.split(' --> ')[0]
    
    return None

def create_embeddings_file(transcript_dir, output_file='embeddings.jsonl'):
    embeddings = {}
    
    # Process each transcript file
    for transcript_file in Path(transcript_dir).glob('*.txt'):
        print(f"Processing {transcript_file.name}...")
        with open(transcript_file, 'r', encoding='utf-8') as f:
            data = f.read().replace("\n", " ")
            # Split into chunks of 500 characters
            chunks = [data[i:i+500] for i in range(0, len(data), 500)]
            
            for chunk in chunks:
                # Get embedding and timestamp for each chunk
                embedding = get_embedding(chunk)
                timestamp = sliding_window_vtt(chunk, str(transcript_file).replace('.txt', '.vtt'))
                
                embeddings[chunk] = {
                    "embedding": embedding,
                    "timestamp": timestamp
                }
    
    # Write embeddings to file
    print("Writing embeddings to file...")
    with open(output_file, 'w') as f:
        for chunk, data in embeddings.items():
            f.write(json.dumps({
                "text": chunk,
                "embedding": data["embedding"],
                "timestamp": data["timestamp"]
            }) + "\n")
    
    return len(embeddings)

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def search_embeddings(query, embeddings_file='embeddings.jsonl'):
    # Get query embedding
    query_embedding = get_embedding(query)
    
    # Load embeddings
    embeddings = {}
    try:
        with open(embeddings_file, 'r') as f:
            for line in f:
                data = json.loads(line)
                embeddings[data['text']] = {
                    'embedding': data['embedding'],
                    'timestamp': data.get('timestamp')  # Handle cases where timestamp might not exist
                }
    except FileNotFoundError:
        return None, None, None, "Embeddings file not found"
    
    # Find best match
    best_chunk = None
    best_score = float("-inf")
    best_timestamp = None
    
    for chunk, data in embeddings.items():
        score = np.dot(data['embedding'], query_embedding)
        if score > best_score:
            best_chunk = chunk
            best_score = score
            best_timestamp = data.get('timestamp')
    
    return best_chunk, best_timestamp, best_score, None 

def verify_embeddings_file(file_path='embeddings.jsonl'):
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline()
            data = json.loads(first_line)
            required_keys = ['text', 'embedding']
            if not all(key in data for key in required_keys):
                return False, "Embeddings file missing required fields"
            return True, "Embeddings file is valid"
    except FileNotFoundError:
        return False, "Embeddings file not found"
    except json.JSONDecodeError:
        return False, "Embeddings file contains invalid JSON"

def process_user_query(query, video_id):
    # Get video-specific embeddings file
    video_dir = Path.cwd() / 'data' / 'user_videos' / video_id
    embeddings_file = video_dir / 'embeddings.jsonl'
    
    print(f"Searching in embeddings file: {embeddings_file}")
    
    # Get the best matching chunk and timestamp
    best_chunk, timestamp, best_score, error = search_embeddings(query, str(embeddings_file))
    
    print(f"Search results: chunk={bool(best_chunk)}, score={best_score}")
    
    if error:
        print(f"Search error: {error}")
        return {"error": error}
    
    if not best_chunk:
        return {"error": "No relevant content found"}
        
    return {
        "chunk": best_chunk,
        "timestamp": timestamp,
        "score": best_score
    }

def initialize_embeddings():
    transcript_dir = "CS410Transcripts/txt"  # Adjust this path as needed
    output_file = "embeddings.jsonl"
    
    if not os.path.exists(output_file):
        print("Creating embeddings file...")
        num_embeddings = create_embeddings_file(transcript_dir, output_file)
        print(f"Created {num_embeddings} embeddings")
    else:
        print("Embeddings file already exists")

def process_transcript(video_id):
    try:
        # Get paths
        video_dir = Path.cwd() / 'data' / 'user_videos' / video_id
        transcript_file = video_dir / 'transcript.vtt'
        embeddings_file = video_dir / 'embeddings.jsonl'
        
        if not transcript_file.exists():
            print(f"Transcript file not found for video {video_id}")
            return False
            
        # Read and process the transcript
        with open(transcript_file, 'r', encoding='utf-8') as f:
            data = f.read().replace("\n", " ")
            # Split into chunks of 500 characters
            chunks = [data[i:i+500] for i in range(0, len(data), 500)]
            
            embeddings = {}
            for chunk in chunks:
                # Get embedding and timestamp for each chunk
                embedding = get_embedding(chunk)
                # Pass the directory containing the VTT file
                timestamp = sliding_window_vtt(chunk, str(video_dir))
                
                if timestamp:
                    embeddings[chunk] = {
                        "embedding": embedding,
                        "timestamp": timestamp
                    }
                else:
                    # If no timestamp found, still store the embedding
                    embeddings[chunk] = {
                        "embedding": embedding,
                        "timestamp": None
                    }
        
        # Write embeddings to file
        with open(embeddings_file, 'w') as f:
            for chunk, data in embeddings.items():
                f.write(json.dumps({
                    "text": chunk,
                    "embedding": data["embedding"],
                    "timestamp": data["timestamp"]
                }) + "\n")
        
        return True
        
    except Exception as e:
        print(f"Error processing transcript: {e}")
        return False

def process_video_query(query, video_id):
    try:
        video_dir = Path.cwd() / 'data' / 'user_videos' / video_id
        embeddings_file = video_dir / 'embeddings.jsonl'
        
        # Get the best matching chunk and timestamp
        best_chunk, timestamp, best_score, error = search_embeddings(query, str(embeddings_file))
        
        if error:
            return {"error": error}
        
        if not best_chunk:
            return {"error": "No relevant content found"}
            
        # Create prompt for GPT
        system_prompt = "You are a friendly and supportive teaching assistant. Your task is to determine whether a user's query is relevant to the video content. If the query is relevant, provide a detailed and accurate answer. If it is not, respond with 'This is not a relevant question. Please ask a different question.'"
        
        prompt = "Answer the question using the following information delimited by triple brackets:\n\n"
        prompt += f"```\n{best_chunk}\n```"
        prompt += "\nQuestion: " + query
        
        # Get GPT response
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4"
        )
        
        response_text = chat_completion.choices[0].message.content
        
        return {
            "response": response_text,
            "timestamp": timestamp,
            "score": best_score
        }
        
    except Exception as e:
        print(f"Error processing video query: {e}")
        return {"error": str(e)}

def process_multiple_videos_query(query, video_ids):
    print("\n=== Starting Search Process ===")
    results = []
    embeddings_file = Path.cwd() / 'data' / 'embeddings' / 'combined_embeddings.jsonl'
    
    if not embeddings_file.exists():
        print("Combined embeddings file not found")
        return []
        
    query_embedding = get_embedding(query)
    temp_results = []
    
    with open(embeddings_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data['video_id'] in video_ids:
                score = np.dot(data['embedding'], query_embedding)
                if score > 0.5:
                    temp_results.append({
                        "video_id": data['video_id'],
                        "response": data['text'],
                        "timestamp": data['timestamp'],
                        "score": float(score)
                    })
    
    # Sort by video_id and timestamp
    temp_results.sort(key=lambda x: (x['video_id'], convertTimestampToSeconds(x['timestamp'])))
    
    # Merge segments that are within 1 minute of each other
    i = 0
    while i < len(temp_results):
        current = temp_results[i]
        merged_response = current['response']
        max_score = current['score']
        j = i + 1
        
        while j < len(temp_results):
            next_result = temp_results[j]
            if (current['video_id'] == next_result['video_id'] and 
                abs(convertTimestampToSeconds(current['timestamp']) - 
                    convertTimestampToSeconds(next_result['timestamp'])) <= 60):
                merged_response += " " + next_result['response']
                max_score = max(max_score, next_result['score'])
                j += 1
            else:
                break
                
        results.append({
            "video_id": current['video_id'],
            "response": merged_response,
            "timestamp": current['timestamp'],
            "score": max_score
        })
        i = j
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]

def convertTimestampToSeconds(timestamp):
    try:
        # Handle timestamps with milliseconds (e.g., "37.889")
        if '.' in timestamp:
            return float(timestamp)
            
        # Handle MM:SS format
        minutes, seconds = map(int, timestamp.split(':'))
        return minutes * 60 + seconds
    except ValueError as e:
        print(f"Error converting timestamp {timestamp}: {str(e)}")
        return 0

def process_all_videos(video_ids):
    print("\n=== Starting Combined Embeddings Processing ===")
    combined_embeddings = []
    embeddings_dir = Path.cwd() / 'data' / 'embeddings'
    embeddings_dir.mkdir(exist_ok=True)
    combined_file = embeddings_dir / 'combined_embeddings.jsonl'
    
    for video_id in video_ids:
        try:
            video_dir = Path.cwd() / 'data' / 'user_videos' / video_id
            transcript_file = video_dir / 'transcript.vtt'
            
            if not transcript_file.exists():
                print(f"Transcript file not found for video {video_id}")
                continue
                
            with open(transcript_file, 'r', encoding='utf-8') as f:
                data = f.read().replace("\n", " ")
                chunks = [data[i:i+500] for i in range(0, len(data), 500)]
                
                for chunk in chunks:
                    embedding = get_embedding(chunk)
                    timestamp = sliding_window_vtt(chunk, str(video_dir))
                    
                    combined_embeddings.append({
                        "text": chunk,
                        "embedding": embedding,
                        "timestamp": timestamp,
                        "video_id": video_id
                    })
        except Exception as e:
            print(f"Error processing video {video_id}: {str(e)}")
            continue
    
    with open(combined_file, 'w') as f:
        for item in combined_embeddings:
            f.write(json.dumps(item) + '\n')
            
    print("=== Finished Processing Combined Embeddings ===")
    return True

def search_combined_embeddings(query):
    embeddings_file = Path.cwd() / 'data' / 'embeddings' / 'combined_embeddings.jsonl'
    
    if not embeddings_file.exists():
        return [], "Embeddings file not found"
        
    query_embedding = get_embedding(query)
    best_matches = []
    
    with open(embeddings_file, 'r') as f:
        for line in f:
            item = json.loads(line)
            score = np.dot(item['embedding'], query_embedding)
            if score > 0.5:
                best_matches.append({
                    "chunk": item['text'],
                    "timestamp": item['timestamp'],
                    "video_id": item['video_id'],
                    "score": float(score)
                })
    
    # Sort by score and return top matches
    best_matches.sort(key=lambda x: x['score'], reverse=True)
    return best_matches[:5]  # Return top 5 matches