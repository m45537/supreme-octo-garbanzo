#!/usr/bin/env python3
"""
Example Usage Script
Demonstrates how to use the Automated Video Generator programmatically
"""

import os
import sys
from pathlib import Path
from auto_video_generator import AutoVideoGenerator
from sheets_handler import GoogleSheetsHandler, setup_sample_sheet


def example_1_basic_usage():
    """
    Example 1: Basic usage - process all pending videos once
    """
    print("\n=== Example 1: Basic Usage ===\n")
    
    # Initialize the generator
    generator = AutoVideoGenerator('config.json')
    generator.initialize_handlers()
    
    # Process all pending videos
    generator.run_once()
    
    print("\n✓ All pending videos processed!")


def example_2_single_video():
    """
    Example 2: Process a single video request directly
    """
    print("\n=== Example 2: Single Video Processing ===\n")
    
    # Initialize
    generator = AutoVideoGenerator('config.json')
    generator.initialize_handlers()
    
    # Create a video request
    video_request = {
        'id': 'example_video_001',
        'topic': 'The Benefits of Morning Exercise',
        'prompts': 'Create an energetic video about morning workouts with upbeat music',
        'status': 'pending'
    }
    
    # Process the video
    result = generator.process_video_request(video_request)
    
    if result['status'] == 'completed':
        print(f"\n✓ Video created successfully!")
        print(f"  YouTube URL: {result['youtube_url']}")
        print(f"  Video File: {result['video_file']}")
    else:
        print(f"\n✗ Video processing failed: {result.get('error')}")


def example_3_batch_processing():
    """
    Example 3: Batch process multiple videos
    """
    print("\n=== Example 3: Batch Processing ===\n")
    
    generator = AutoVideoGenerator('config.json')
    generator.initialize_handlers()
    
    # List of videos to create
    videos = [
        {
            'id': 'batch_001',
            'topic': '5 Quick Productivity Hacks',
            'prompts': 'Fast-paced video with modern graphics'
        },
        {
            'id': 'batch_002',
            'topic': 'Understanding Climate Change',
            'prompts': 'Educational video with data visualizations'
        },
        {
            'id': 'batch_003',
            'topic': 'Beginner\'s Guide to Photography',
            'prompts': 'Friendly tutorial with photo examples'
        }
    ]
    
    results = []
    for video in videos:
        print(f"\nProcessing: {video['topic']}")
        try:
            result = generator.process_video_request(video)
            results.append(result)
            print(f"  Status: {result['status']}")
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    # Summary
    completed = sum(1 for r in results if r['status'] == 'completed')
    print(f"\n✓ Batch complete: {completed}/{len(videos)} videos successful")


def example_4_custom_config():
    """
    Example 4: Use custom configuration
    """
    print("\n=== Example 4: Custom Configuration ===\n")
    
    # Create custom config
    custom_config = {
        "google_sheets": {
            "spreadsheet_id": "YOUR_SPREADSHEET_ID",
            "input_sheet": "Video Ideas",
            "output_sheet": "Generated Videos",
            "credentials_path": "google_credentials.json"
        },
        "video_generation": {
            "ai_provider": "anthropic",  # Use Claude instead of GPT
            "video_duration": 45,  # Shorter videos
            "resolution": "1280x720",  # Lower resolution
            "fps": 30
        },
        "youtube": {
            "client_secrets_file": "client_secrets.json",
            "default_category": "27",  # Education
            "privacy_status": "unlisted"  # Unlisted instead of private
        },
        "error_handling": {
            "max_retries": 5,  # More retries
            "retry_delay": 10
        }
    }
    
    # Save custom config
    import json
    with open('custom_config.json', 'w') as f:
        json.dump(custom_config, f, indent=2)
    
    # Use custom config
    generator = AutoVideoGenerator('custom_config.json')
    print("✓ Generator initialized with custom config")


def example_5_monitoring():
    """
    Example 5: Monitor video processing with callbacks
    """
    print("\n=== Example 5: Monitoring with Callbacks ===\n")
    
    class MonitoredGenerator(AutoVideoGenerator):
        """Extended generator with monitoring"""
        
        def on_video_start(self, video_data):
            print(f"🎬 Starting: {video_data['topic']}")
        
        def on_video_complete(self, result):
            print(f"✓ Completed: {result['topic']}")
            print(f"  URL: {result['youtube_url']}")
        
        def on_video_error(self, video_data, error):
            print(f"✗ Error: {video_data['topic']}")
            print(f"  {str(error)}")
        
        def process_video_request(self, row_data):
            self.on_video_start(row_data)
            try:
                result = super().process_video_request(row_data)
                if result['status'] == 'completed':
                    self.on_video_complete(result)
                else:
                    self.on_video_error(row_data, result.get('error'))
                return result
            except Exception as e:
                self.on_video_error(row_data, e)
                raise
    
    # Use monitored generator
    generator = MonitoredGenerator('config.json')
    generator.initialize_handlers()
    print("✓ Monitoring enabled")


def example_6_sheets_setup():
    """
    Example 6: Set up Google Sheets with sample data
    """
    print("\n=== Example 6: Google Sheets Setup ===\n")
    
    # Initialize sheets handler
    handler = GoogleSheetsHandler(
        credentials_path='google_credentials.json',
        spreadsheet_id='YOUR_SPREADSHEET_ID'
    )
    
    # Create sheets
    handler.create_sheet_if_not_exists("Video Ideas")
    handler.create_sheet_if_not_exists("Generated Videos")
    handler.create_sheet_if_not_exists("Error Log")
    
    # Add sample data
    setup_sample_sheet(handler)
    
    print("✓ Sheets created with sample data")


def example_7_continuous_mode():
    """
    Example 7: Run in continuous mode
    """
    print("\n=== Example 7: Continuous Mode ===\n")
    print("This will run continuously, checking for new videos every 60 seconds")
    print("Press Ctrl+C to stop\n")
    
    generator = AutoVideoGenerator('config.json')
    generator.initialize_handlers()
    
    try:
        generator.run_continuous(check_interval=60)
    except KeyboardInterrupt:
        print("\n\n✓ Stopped by user")


def main():
    """Main menu"""
    examples = {
        '1': ('Basic usage - process all pending videos', example_1_basic_usage),
        '2': ('Process a single video', example_2_single_video),
        '3': ('Batch process multiple videos', example_3_batch_processing),
        '4': ('Use custom configuration', example_4_custom_config),
        '5': ('Monitor video processing', example_5_monitoring),
        '6': ('Set up Google Sheets', example_6_sheets_setup),
        '7': ('Run in continuous mode', example_7_continuous_mode),
    }
    
    print("\n" + "=" * 60)
    print("  🎬 Automated Video Generator - Examples")
    print("=" * 60)
    
    print("\nSelect an example to run:\n")
    for key, (description, _) in examples.items():
        print(f"  {key}. {description}")
    print("  q. Quit")
    
    choice = input("\nYour choice: ").strip().lower()
    
    if choice == 'q':
        print("\nGoodbye!")
        sys.exit(0)
    
    if choice in examples:
        try:
            examples[choice][1]()
        except Exception as e:
            print(f"\n✗ Error running example: {str(e)}")
            print("\nMake sure you have:")
            print("  1. Installed all dependencies (pip install -r requirements.txt)")
            print("  2. Configured API keys in .env")
            print("  3. Set up Google Sheets credentials")
            print("  4. Set up YouTube credentials")
            print("  5. Updated config.json with your spreadsheet ID")
    else:
        print("\nInvalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExited by user")
        sys.exit(0)
