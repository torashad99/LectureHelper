import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import re
import numpy as np
import webvtt
from typing import List

load_dotenv()

client = OpenAI(api_key=os.environ["OPEN_AI_API_KEY"])

def sliding_window_vtt(best_chunk, vtt_directory):
    # Normalize the search text
    search_text = ' '.join(best_chunk.lower().split())
    
    for vtt_file in Path(vtt_directory).glob('L*.vtt'):
        try:
            captions = list(webvtt.read(vtt_file))
            if not captions:
                continue

            # Build concatenated text with timestamps
            for i in range(len(captions)):
                concatenated_text = ""
                for j in range(i, min(i + 5, len(captions))):
                    if concatenated_text:
                        concatenated_text += ' '
                    concatenated_text += captions[j].text.lower()

                if "document ranking" in concatenated_text or "rank these relevant documents" in concatenated_text:
                    return vtt_file.stem, captions[i].start

        except Exception as e:
            print(f"Error processing {vtt_file}: {e}")
            continue
            
    return None, None

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
        transcript_file = video_dir / 'transcript.txt'
        embeddings_file = video_dir / 'embeddings.jsonl'
        
        if not transcript_file.exists():
            print(f"Transcript file not found for video {video_id}")
            return False
            
        # Read and process the transcript
        with open(transcript_file, 'r', encoding='utf-8') as f:
            data = f.read()
            chunks = [data[i:i+500] for i in range(0, len(data), 500)]
            
            embeddings = {}
            for chunk in chunks:
                # Get embedding and timestamp for each chunk
                embedding = get_embedding(chunk)
                # Still use VTT for timestamp lookup
                timestamp = sliding_window_vtt(chunk, str(video_dir))
                
                embeddings[chunk] = {
                    "embedding": embedding,
                    "timestamp": timestamp or None
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
    print(f"Looking for videos: {video_ids}")
    embeddings_file = Path.cwd() / 'data' / 'embeddings' / 'combined_embeddings.jsonl'
    
    # Load all embeddings first
    embeddings = {}
    with open(embeddings_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data['video_id'] in video_ids:
                embeddings[data['text']] = {
                    'embedding': data['embedding'],
                    'video_id': data['video_id']
                }
    
    # Get query embedding
    query_embedding = get_embedding(query)
    
    # Find best matches
    matches = []
    for chunk, data in embeddings.items():
        score = np.dot(data['embedding'], query_embedding)
        if score > 0.5:  # Keep threshold for relevance
            matches.append({
                "text": chunk,
                "video_id": data['video_id'],
                "score": float(score)
            })
    
    # Sort by score
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Process top matches
    temp_results = []
    vtt_dir = Path.cwd() / 'CS410Transcripts' / 'vtt'
    system_prompt = "You are a friendly and supportive teaching assistant for a course on Text Information Systems."
    
    # Take top 5 matches
    for match in matches[:5]:
        try:
            lecture_index, found_timestamp = sliding_window_vtt(match['text'], str(vtt_dir))
            if lecture_index and found_timestamp and lecture_index == match['video_id']:
                prompt = f"Answer the question using the following information:\n\n{match['text']}\n\nQuestion: {query}"
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model="gpt-4"
                )
                
                temp_results.append({
                    "video_id": match['video_id'],
                    "response": chat_completion.choices[0].message.content,
                    "timestamp": found_timestamp,
                    "score": match['score']
                })
                
        except Exception as e:
            print(f"Error processing match: {e}")
            continue
    
    print(f"\nFound {len(temp_results)} results")
    return temp_results

def find_timestamp_in_vtt(chunk: str, vtt_file: str) -> str:
    """
    Find timestamp for a chunk of text in VTT file using webvtt-py
    """
    try:
        if not Path(vtt_file).exists():
            print(f"VTT file not found: {vtt_file}")
            return None
            
        timestamps = reverseSearchText(vtt_file, chunk)
        if timestamps:
            return timestamps[0]  # Return first matching timestamp
        return None
        
    except Exception as e:
        print(f"Error finding timestamp: {e}")
        return None

def reverseSearchText(file_path: str, text_chunk: str) -> List[str]:
    """
    Searches for the text_chunk in the VTT file and returns the associated start timestamp(s).
    """
    timestamps = []
    try:
        captions = list(webvtt.read(file_path))
        if not captions:
            return timestamps

        # Normalize the search text
        search_text = ' '.join(text_chunk.lower().split())
        
        # Normalize captions' texts
        normalized_captions = [' '.join(caption.text.lower().split()) for caption in captions]
        start_times = [caption.start for caption in captions]

        n = len(captions)
        
        # Iterate through each caption
        for i in range(n):
            concatenated_text = ""
            for j in range(i, n):
                if concatenated_text:
                    concatenated_text += ' '
                concatenated_text += normalized_captions[j]

                if concatenated_text.startswith(search_text):
                    timestamps.append(start_times[i])
                    break

                if len(concatenated_text) >= len(search_text):
                    break

        return list(dict.fromkeys(timestamps))

    except Exception as e:
        print(f"An error occurred while parsing the VTT file: {e}")
        return []

def convertTimestampToSeconds(timestamp):
    try:
        # Handle HH:MM:SS.mmm format
        if ':' in timestamp:
            parts = timestamp.split(':')
            if len(parts) == 3:  # HH:MM:SS.mmm
                hours, minutes, seconds = parts
                seconds = float(seconds)
                return int(hours) * 3600 + int(minutes) * 60 + seconds
            elif len(parts) == 2:  # MM:SS.mmm
                minutes, seconds = parts
                seconds = float(seconds)
                return int(minutes) * 60 + seconds
        # Handle decimal seconds format
        return float(timestamp)
        
    except (ValueError, TypeError) as e:
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
            transcript_file = video_dir / 'transcript.txt'
            
            if not transcript_file.exists():
                print(f"Transcript file not found for video {video_id}")
                continue
                
            with open(transcript_file, 'r', encoding='utf-8') as f:
                data = f.read()
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

def init_lecture_embeddings():
    print("\n=== Initializing CS410 Lecture Embeddings ===")
    embeddings_dir = Path.cwd() / 'data' / 'embeddings'
    combined_file = embeddings_dir / 'combined_embeddings.jsonl'
    
    if combined_file.exists():
        print("Embeddings file already exists, skipping initialization")
        return True
        
    embeddings_dir.mkdir(exist_ok=True)
    
