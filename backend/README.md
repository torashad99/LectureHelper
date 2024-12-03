# Video Search System Documentation

## Overview
This system adapts semantic search techniques from CS410 to enable efficient searching across multiple video transcripts using OpenAI embeddings.

## Requirements
- Python 3.x
- OpenAI API Key
- Dependencies from requirements.txt

## Installation 
bash
pip install -r requirements.txt


## Core Components

### 1. Embedding Generation (`process_all_videos`)
Processes video transcripts into searchable embeddings:
- Chunks text into 500-character segments
- Generates embeddings using OpenAI's text-embedding-3-small model
- Stores video_id with each embedding
- Creates combined JSONL file for efficient searching

Reference: 
python:backend/services/embedding_service.py

startLine: 320
endLine: 359


### 2. Search Implementation (`process_multiple_videos_query`) 
Multi-video semantic search with context merging:
- Searches across multiple videos simultaneously
- Merges nearby segments (within 60 seconds)
- Returns top 5 most relevant results
- Maintains timestamp accuracy

Reference:
python:backend/services/embedding_service.py

startLine: 248
endLine: 301


### 3. Timestamp Handling (`sliding_window_vtt`)
Accurate timestamp extraction from VTT files:
- Uses 5-word sliding window
- Case-insensitive matching
- Handles various VTT formats
- Returns nearest timestamp

Reference:
python:backend/services/embedding_service.py
startLine: 13
endLine: 35


## Usage

### Processing Videos
python
from services.embedding_service import process_all_videos
Process multiple videos
success = process_all_videos(['video_id1', 'video_id2'])


### Searching Content

python
from services.embedding_service import process_multiple_videos_query
Search across videos
results = process_multiple_videos_query("search query", ['video_id1', 'video_id2'])

## Data Structure

### Combined Embeddings File
json
{
"text": "transcript chunk",
"embedding": [float array],
"timestamp": "MM:SS",
"video_id": "unique_identifier"
}


### Search Results
json
{
"video_id": "video identifier",
"response": "merged transcript text",
"timestamp": "MM:SS",
"score": 0.85
}



## Configuration

### Default Settings
- Embedding model: text-embedding-3-small
- Chunk size: 500 characters
- Similarity threshold: 0.5
- Timestamp merge window: 60 seconds
- Results limit: 5

### File Structure

backend/
├── data/
│ ├── embeddings/
│ │ └── combined_embeddings.jsonl
│ └── user_videos/
│ └── [video_id]/
│ └── transcript.vtt
└── services/
└── embedding_service.py


## Error Handling
The system includes comprehensive error handling for:
- Missing transcript files
- Invalid JSON in embeddings
- OpenAI API failures
- File system errors

## Performance Considerations
- Combined embeddings file for faster searching
- Early filtering by video_id
- Efficient timestamp merging
- Dot product similarity calculations

## Limitations
- Requires VTT format transcripts
- Dependent on OpenAI API availability
- Fixed chunk size may split sentences
- Memory usage scales with number of videos

## Future Improvements
1. Implement embedding caching
2. Add parallel processing
3. Dynamic chunk sizing
4. Configurable similarity thresholds
5. Advanced context merging

## Credits
Based on CS410 course materials and adapted for multi-video search functionality.

## License
MIT License - See LICENSE file for details