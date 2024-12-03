# Video Search System Adaptations

## Overview
This document details how we adapted the CS410 example code to create a multi-video search system.

## Key Adaptations

### 1. Search Implementation
Based on `examples/embeddings/openai/05_text.py`:
```
python
# Example usage
vtt_directory = '../../../CS410Transcripts/vtt'
best_chunk = "st be judged by the users second document ranking is generally preferred and this will help users prioritize examination of search without and this is also the bypass the difficulty in determining absolute relevance because we can get some help from users in determining where to make the cutoff it's more flexible so this further suggests that the main technical channeling in designing and so changing is redesigned effective ranking function in other word"

lecture_index, start_time = sliding_window_vtt(best_chunk, vtt_directory)

if lecture_index and start_time:
    lecture_number = int(lecture_index[1:])
    print(f"This came from Lecture {lecture_number}, which the professor talks about the topic around {start_time}.")
else:
    print("Could not find a matching timestamp in the VTT files.")
```
### 2. Timestamp Handling
Adapted from original VTT search:

```python
def sliding_window_vtt(best_chunk, vtt_directory):
    # Split the best chunk into words
    words = best_chunk.split()
    # Start from the second word for the sliding window
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
                    # Find the subtitle number and timestamp
                    lines = content[:match.start()].split('\n')
                    subtitle_number = None
                    timestamp = None
                    
                    for line in reversed(lines):
                        if '-->' in line:
                            timestamp = line.split(' --> ')[0]
                        elif line.strip().isdigit():
                            subtitle_number = int(line.strip())
                            break
                    
                    if subtitle_number and timestamp:
                        lecture_index = vtt_file.stem
                        return lecture_index, timestamp
    
    return None, None
```

Changes:
- Simplified to work with single VTT file per video
- Removed lecture number handling
- Added error handling for missing timestamps
- Maintained sliding window approach for accuracy

## Key Differences from Examples

1. Multi-video Support
- Original: Single document search
- Adapted: Combined embeddings from multiple videos
- Implementation: Added video_id tracking and filtering

2. Results Processing
- Original: Single best match
- Adapted: Multiple matches with context merging
- Implementation: 60-second window merging

3. File Structure
- Original: Separate embeddings per document
- Adapted: Combined JSONL file
- Implementation: Unified storage for faster searching

4. Error Handling
- Original: Basic file checks
- Adapted: Comprehensive error handling
- Implementation: Added try-catch blocks and validation

## Performance Improvements
- Combined embeddings file vs separate files
- Early filtering by video_id
- Efficient timestamp merging
- Maintained original dot product similarity

## Credits
Based on CS410 course materials, specifically:
- `examples/embeddings/juliastuff/changed_embeddings_maker.py`
- `examples/embeddings/openai/05_text.py`