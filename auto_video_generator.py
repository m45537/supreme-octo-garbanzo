"""
Automated Video Generation System
Drop a video idea in Google Sheets and automatically generate, upload, and log YouTube videos.
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, Optional, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoVideoGenerator:
    """Main orchestrator for automated video generation workflow"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the video generator with configuration"""
        self.config = self.load_config(config_path)
        self.sheets_handler = None
        self.video_generator = None
        self.youtube_uploader = None
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "google_sheets": {
                "spreadsheet_id": "",
                "input_sheet": "Video Ideas",
                "output_sheet": "Generated Videos",
                "credentials_path": "credentials.json"
            },
            "video_generation": {
                "ai_provider": "openai",  # or "anthropic", "elevenlabs", etc.
                "video_duration": 60,
                "resolution": "1920x1080",
                "fps": 30
            },
            "youtube": {
                "client_secrets_file": "client_secrets.json",
                "default_category": "22",  # People & Blogs
                "privacy_status": "private"  # or "public", "unlisted"
            },
            "error_handling": {
                "max_retries": 3,
                "retry_delay": 5
            }
        }
    
    def initialize_handlers(self):
        """Initialize all service handlers"""
        from sheets_handler import GoogleSheetsHandler
        from video_generator import VideoGenerator
        from youtube_uploader import YouTubeUploader
        
        self.sheets_handler = GoogleSheetsHandler(
            self.config['google_sheets']['credentials_path'],
            self.config['google_sheets']['spreadsheet_id']
        )
        
        self.video_generator = VideoGenerator(
            self.config['video_generation']
        )
        
        self.youtube_uploader = YouTubeUploader(
            self.config['youtube']['client_secrets_file']
        )
    
    def process_video_request(self, row_data: Dict) -> Dict:
        """
        Process a single video request from Google Sheets
        
        Args:
            row_data: Dictionary containing video topic and prompts
            
        Returns:
            Dictionary with processing results
        """
        video_id = row_data.get('id', str(int(time.time())))
        topic = row_data.get('topic', '')
        prompts = row_data.get('prompts', '')
        
        logger.info(f"Processing video request: {topic}")
        
        result = {
            'id': video_id,
            'topic': topic,
            'status': 'pending',
            'error': None,
            'video_url': None,
            'video_file': None,
            'youtube_url': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Step 1: Get Music and Intro Video
            logger.info("Step 1: Generating music and intro video")
            music_intro = self.video_generator.create_music_and_intro(topic, prompts)
            result['music_file'] = music_intro.get('music_path')
            result['intro_file'] = music_intro.get('intro_path')
            
            # Step 2: Generate Full Video
            logger.info("Step 2: Generating full video")
            video_data = self.video_generator.generate_full_video(
                topic=topic,
                prompts=prompts,
                music_path=music_intro.get('music_path'),
                intro_path=music_intro.get('intro_path')
            )
            result['video_file'] = video_data['video_path']
            result['video_url'] = video_data.get('video_url')
            
            # Step 3: Upload to YouTube
            logger.info("Step 3: Uploading to YouTube")
            youtube_result = self.youtube_uploader.upload_video(
                video_path=video_data['video_path'],
                title=topic,
                description=f"Generated video about: {topic}\n\n{prompts}",
                category=self.config['youtube']['default_category'],
                privacy_status=self.config['youtube']['privacy_status']
            )
            result['youtube_url'] = youtube_result['url']
            result['youtube_id'] = youtube_result['id']
            
            result['status'] = 'completed'
            logger.info(f"Video processing completed: {result['youtube_url']}")
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}", exc_info=True)
            result['status'] = 'failed'
            result['error'] = str(e)
            
            # Handle errors with retry logic
            result = self.handle_error(result, row_data)
        
        return result
    
    def handle_error(self, result: Dict, row_data: Dict) -> Dict:
        """
        Handle errors with retry logic
        
        Args:
            result: Current result dictionary with error
            row_data: Original row data
            
        Returns:
            Updated result dictionary
        """
        max_retries = self.config['error_handling']['max_retries']
        retry_count = row_data.get('retry_count', 0)
        
        if retry_count < max_retries:
            logger.info(f"Retrying video generation (attempt {retry_count + 1}/{max_retries})")
            time.sleep(self.config['error_handling']['retry_delay'])
            
            # Update retry count and try again
            row_data['retry_count'] = retry_count + 1
            return self.process_video_request(row_data)
        else:
            logger.error(f"Max retries reached for video: {row_data.get('topic')}")
            result['status'] = 'failed_max_retries'
            
            # Log error to sheets
            self.log_error(result)
            
        return result
    
    def log_error(self, result: Dict):
        """Log error to error tracking sheet"""
        try:
            error_data = {
                'timestamp': result['timestamp'],
                'video_id': result['id'],
                'topic': result['topic'],
                'error': result['error'],
                'status': result['status']
            }
            self.sheets_handler.append_to_sheet('Error Log', [error_data])
        except Exception as e:
            logger.error(f"Failed to log error to sheets: {str(e)}")
    
    def mark_as_done(self, result: Dict):
        """Mark video as completed in Google Sheets"""
        try:
            self.sheets_handler.append_to_sheet(
                self.config['google_sheets']['output_sheet'],
                [result]
            )
            logger.info(f"Marked video as done: {result['id']}")
        except Exception as e:
            logger.error(f"Failed to mark as done: {str(e)}")
    
    def run_once(self):
        """Process all pending video requests once"""
        logger.info("Starting video generation run")
        
        # Get pending videos from Google Sheets
        pending_videos = self.sheets_handler.get_pending_videos(
            self.config['google_sheets']['input_sheet']
        )
        
        logger.info(f"Found {len(pending_videos)} pending videos")
        
        for video_data in pending_videos:
            try:
                result = self.process_video_request(video_data)
                self.mark_as_done(result)
            except Exception as e:
                logger.error(f"Unexpected error processing video: {str(e)}", exc_info=True)
    
    def run_continuous(self, check_interval: int = 60):
        """
        Run continuously, checking for new videos at regular intervals
        
        Args:
            check_interval: Seconds between checks for new videos
        """
        logger.info(f"Starting continuous video generation (checking every {check_interval}s)")
        
        while True:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"Error in continuous run: {str(e)}", exc_info=True)
            
            logger.info(f"Waiting {check_interval} seconds before next check")
            time.sleep(check_interval)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Video Generation System')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--mode', choices=['once', 'continuous'], default='once',
                      help='Run once or continuously')
    parser.add_argument('--interval', type=int, default=60,
                      help='Check interval in seconds (for continuous mode)')
    
    args = parser.parse_args()
    
    # Initialize the generator
    generator = AutoVideoGenerator(args.config)
    generator.initialize_handlers()
    
    # Run based on mode
    if args.mode == 'once':
        generator.run_once()
    else:
        generator.run_continuous(args.interval)


if __name__ == "__main__":
    main()
