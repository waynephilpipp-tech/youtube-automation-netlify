#!/usr/bin/env python3
import os
import json
import yt_dlp
import logging
import sys
from datetime import datetime

def handler(event, context):
    """Netlify function handler"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    try:
        # Get environment variables
        channel_url = os.environ.get('CHANNEL_URL', '')
        if not channel_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'CHANNEL_URL not set'})
            }
        
        logging.info("🎬 Starting video download test...")
        logging.info(f"📺 Channel: {channel_url}")
        
        # Create temp directory
        download_folder = "/tmp/videos"
        os.makedirs(download_folder, exist_ok=True)
        
        # yt-dlp options for testing (download only 1-2 videos)
        ydl_opts = {
            'outtmpl': f'{download_folder}/%(title)s_%(id)s.%(ext)s',
            'format': 'best[ext=mp4]/best',
            'writeinfojson': True,
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'playlist_items': '1-2',  # Only download first 2 videos for testing
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logging.info("📊 Extracting channel info...")
            
            # Extract info without downloading first
            info = ydl.extract_info(channel_url, download=False)
            
            if 'entries' not in info:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'No videos found on channel'})
                }
            
            # Get video count
            total_videos = len(list(info['entries']))
            logging.info(f"📺 Found {total_videos} total videos")
            
            # Download first 2 videos for testing
            logging.info("📥 Starting test download (first 2 videos)...")
            ydl.download([channel_url])
            
            # Check downloaded files
            downloaded_files = os.listdir(download_folder)
            video_files = [f for f in downloaded_files if f.endswith('.mp4')]
            
            logging.info(f"✅ Downloaded {len(video_files)} video files")
            
            # File size info
            total_size = 0
            for file in video_files:
                file_path = os.path.join(download_folder, file)
                file_size = os.path.getsize(file_path)
                total_size += file_size
                logging.info(f"📁 {file}: {file_size / (1024*1024):.1f} MB")
            
            result = {
                'success': True,
                'total_videos_on_channel': total_videos,
                'downloaded_count': len(video_files),
                'total_size_mb': round(total_size / (1024*1024), 1),
                'files': video_files,
                'timestamp': datetime.now().isoformat()
            }
            
            logging.info("🎉 Test completed successfully!")
            
            return {
                'statusCode': 200,
                'body': json.dumps(result, indent=2)
            }
            
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logging.error(error_msg)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            })
        }

# For local testing
if __name__ == "__main__":
    # Mock event and context for local testing
    test_event = {}
    test_context = {}
    
    result = handler(test_event, test_context)
    print(json.dumps(result, indent=2))
