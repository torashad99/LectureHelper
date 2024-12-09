import yt_dlp
import os
from pathlib import Path
import json
from youtube_transcript_api import YouTubeTranscriptApi

class VideoProcessor:
    def process_video(self, youtube_url):
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True
            }
            
            # Get video info
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                video_info = ydl.extract_info(youtube_url, download=False)
                
            video_id = video_info['id']
            
            # Check if video already exists
            video_dir = Path.cwd() / 'data' / 'user_videos' / video_id
            if video_dir.exists():
                raise ValueError('This video has already been uploaded')
            
            video_title = video_info['title']
            
            # Create directory for new video
            dir_path = Path.cwd() / 'data' / 'user_videos' / video_id
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Get transcript and save both VTT and clean text versions
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                
                # Save VTT version
                vtt_content = self._convert_to_vtt(transcript)
                vtt_path = dir_path / 'transcript.vtt'
                with open(vtt_path, 'w', encoding='utf-8') as f:
                    f.write(vtt_content)
                    
                # Save clean text version
                text_content = ' '.join(item['text'] for item in transcript)
                text_path = dir_path / 'transcript.txt'
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                    
            except Exception as e:
                print(f"Error getting transcript: {e}")
                raise e

            # Save metadata
            metadata = {
                'id': video_id,
                'title': video_title,
                'url': youtube_url
            }
            
            metadata_path = dir_path / 'metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return metadata
            
        except Exception as e:
            print(f'Error processing video: {e}')
            raise e

    def _convert_to_vtt(self, transcript):
        vtt = "WEBVTT\n\n"
        for i, item in enumerate(transcript):
            # Convert start time from seconds to HH:MM:SS.mmm
            start_time = self._format_time(item['start'])
            end_time = self._format_time(item['start'] + item['duration'])
            
            vtt += f"{i+1}\n"
            vtt += f"{start_time} --> {end_time}\n"
            vtt += f"{item['text']}\n\n"
        return vtt

    def _format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

# Create singleton instance
video_processor = VideoProcessor() 