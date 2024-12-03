import re
from pathlib import Path

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

# Example usage
vtt_directory = '../../../CS410Transcripts/vtt'
best_chunk = "st be judged by the users second document ranking is generally preferred and this will help users prioritize examination of search without and this is also the bypass the difficulty in determining absolute relevance because we can get some help from users in determining where to make the cutoff it's more flexible so this further suggests that the main technical channeling in designing and so changing is redesigned effective ranking function in other word"

lecture_index, start_time = sliding_window_vtt(best_chunk, vtt_directory)

if lecture_index and start_time:
    lecture_number = int(lecture_index[1:])
    print(f"This came from Lecture {lecture_number}, which the professor talks about the topic around {start_time}.")
else:
    print("Could not find a matching timestamp in the VTT files.")