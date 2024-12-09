from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path

def download_transcript(video_id):
    """Downloads both clean transcript and VTT files"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        video_dir = Path.cwd() / 'data' / 'user_videos' / video_id
        video_dir.mkdir(parents=True, exist_ok=True)
        
        # Save clean transcript
        clean_text = ' '.join([entry['text'] for entry in transcript])
        with open(video_dir / 'transcript.txt', 'w', encoding='utf-8') as f:
            f.write(clean_text)
            
        # Save VTT
        vtt_content = "WEBVTT\n\n"
        for entry in transcript:
            start = entry['start']
            duration = entry['duration']
            end = start + duration
            text = entry['text']
            
            start_time = f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{start%60:06.3f}"
            end_time = f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{end%60:06.3f}"
            vtt_content += f"{start_time} --> {end_time}\n{text}\n\n"
            
        with open(video_dir / 'transcript.vtt', 'w', encoding='utf-8') as f:
            f.write(vtt_content)
            
        return True
    except Exception as e:
        print(f"Error downloading transcript: {e}")
        return False 