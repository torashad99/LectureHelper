# Video Search System Adaptations

## Overview
This document details how we adapted the CS410 example code to create a multi-video search system.

## Original Example Code

### 1. Basic Embedding Generation
```python:examples/embeddings/openai/01_create_embeddings.py
def process_file(file_path):
    with open(file_path, "r") as f:
        data = f.read().replace("\n", " ")
        chunks = [data[i:i+500] for i in range(0, len(data), 500)]
        embeddings = {}
        for chunk in chunks:
            embeddings[chunk] = get_embedding(chunk)
    return embeddings
```

### 2. Single Video Search
From `examples/embeddings/openai/05_text.py`:

```python:examples/embeddings/openai/05_text.py

def sliding_window_vtt(best_chunk, vtt_directory):
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

```

### 3. Original Timestamp Search
From `examples/embeddings/openai/04_reverse_search.py`:

```python:examples/embeddings/openai/04_reverse_search.py
def find_timestamp_in_vtt(chunk, vtt_directory):
    first_five_words = ' '.join(chunk.split()[:5])
    pattern = re.compile(re.escape(first_five_words), re.IGNORECASE)
    
    for vtt_file in Path(vtt_directory).glob('L*.vtt'):
        lecture_index = vtt_file.stem
        with open(vtt_file, 'r', encoding='utf-8') as f:
```

## Our Adaptations

### 1. Multi-Video Embedding Generation

```python:backend/services/embedding_service.py
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
```

Key Changes:
- Added video_id tracking
- Combined embeddings from multiple videos
- Unified storage in single JSONL file
- Added error handling

### 2. Multi-Video Search

```python:backend/services/embedding_service.py
def process_multiple_videos_query(query, video_ids):
    print("\n=== Starting Search Process ===")
    results = []
    embeddings_file = Path.cwd() / 'data' / 'embeddings' / 'combined_embeddings.jsonl'
    
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
```

Key Changes:
- Multi-video filtering
- Similarity threshold of 0.5
- Added score tracking
- Result merging within 60 seconds

### 3. Simplified Timestamp Search

```python:backend/services/embedding_service.py
def sliding_window_vtt(best_chunk, vtt_directory):
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
```

Key Changes:
- Removed lecture number handling
- Simplified for single VTT per video
- Maintained sliding window approach
- Added error handling

## Major Improvements

1. Multi-Video Support
- Original: Single file processing
- New: Combined embeddings with video_id tracking

2. Search Capabilities  
- Original: Basic similarity matching
- New: Multi-video search with context merging

3. Error Handling
- Original: Basic file checks
- New: Comprehensive error handling and validation

4. Storage Efficiency
- Original: Separate files per video
- New: Combined JSONL with efficient filtering

## Credits
Based on CS410 course materials, specifically:
- `examples/embeddings/openai/01_create_embeddings.py`
- `examples/embeddings/openai/04_reverse_search.py`
- `examples/embeddings/openai/05_text.py`