from pathlib import Path
import re

def sliding_window_vtt(chunk, vtt_directory):
    """
    Reference to original sliding window implementation:
    """
    # Reference to original implementation
    words = chunk.split()
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