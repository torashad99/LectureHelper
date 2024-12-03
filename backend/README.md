# Video Search System Adaptations

## Overview
This document details how we adapted the CS410 example code to create a multi-video search system.

## Key Adaptations

### 1. Embedding Generation
Based on `examples/embeddings/juliastuff/changed_embeddings_maker.py`:
```
python
startLine: 118
endLine: 156
```

### 2. Search Implementation
Based on `examples/embeddings/openai/05_text.py`:
```
python
startLine: 39
endLine: 49
```
### 3. Timestamp Handling
Adapted from original VTT search:

```python
startLine: 13
endLine: 35
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