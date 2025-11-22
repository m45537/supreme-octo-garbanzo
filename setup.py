#!/usr/bin/env python3
"""
Setup script for Automated Video Generator
Helps configure API keys, credentials, and test the system
"""

import os
import sys
import json
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✓ {description}: Found")
        return True
    else:
        print(f"✗ {description}: Missing")
        return False


def create_env_file():
    """Create .env file for API keys"""
    print_header("API Keys Setup")
    
    env_path = Path(".env")
    
    if env_path.exists():
        print("⚠️  .env file already exists. Do you want to overwrite it? (y/n): ", end="")
        if input().lower() != 'y':
            print("Skipping .env creation")
            return
    
    print("\nPlease enter your API keys (press Enter to skip):")
    
    openai_key = input("OpenAI API Key: ").strip()
    anthropic_key = input("Anthropic API Key: ").strip()
    
    with open(env_path, 'w') as f:
        f.write("# API Keys for Automated Video Generator\n\n")
        if openai_key:
            f.write(f"OPENAI_API_KEY={openai_key}\n")
        if anthropic_key:
            f.write(f"ANTHROPIC_API_KEY={anthropic_key}\n")
        
        f.write("\n# Add other API keys as needed:\n")
        f.write("# ELEVENLABS_API_KEY=your_key_here\n")
        f.write("# REPLICATE_API_TOKEN=your_token_here\n")
    
    print(f"\n✓ Created {env_path}")


def setup_google_sheets():
    """Guide user through Google Sheets setup"""
    print_header("Google Sheets Setup")
    
    print("To use Google Sheets for input/output:")
    print("\n1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print("\n2. Create a new project (or select existing)")
    print("\n3. Enable Google Sheets API")
    print("\n4. Create a Service Account:")
    print("   - Go to IAM & Admin > Service Accounts")
    print("   - Create Service Account")
    print("   - Grant 'Editor' role")
    print("   - Create and download JSON key")
    print("\n5. Save the JSON key as 'google_credentials.json'")
    print("\n6. Share your Google Sheet with the service account email")
    print("   (found in the JSON file)")
    
    if not check_file_exists('google_credentials.json', 'Google Credentials'):
        print("\n⚠️  Place your credentials file in this directory as 'google_credentials.json'")


def setup_youtube():
    """Guide user through YouTube API setup"""
    print_header("YouTube API Setup")
    
    print("To upload videos to YouTube:")
    print("\n1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print("\n2. Use the same project as Google Sheets (or create new)")
    print("\n3. Enable YouTube Data API v3")
    print("\n4. Create OAuth 2.0 Credentials:")
    print("   - Go to APIs & Services > Credentials")
    print("   - Create OAuth 2.0 Client ID")
    print("   - Application type: Desktop app")
    print("   - Download the JSON file")
    print("\n5. Save it as 'client_secrets.json'")
    
    if not check_file_exists('client_secrets.json', 'YouTube OAuth Credentials'):
        print("\n⚠️  Place your OAuth credentials as 'client_secrets.json'")
    
    print("\n📘 Detailed guide:")
    print("   https://developers.google.com/youtube/v3/getting-started")


def configure_spreadsheet():
    """Help user configure their spreadsheet"""
    print_header("Google Spreadsheet Configuration")
    
    print("Your Google Sheet should have the following structure:")
    print("\n📊 Sheet: 'Video Ideas' (Input)")
    print("   Columns: ID | Topic | Prompts | Status")
    print("\n📊 Sheet: 'Generated Videos' (Output)")
    print("   Columns: ID | Topic | Status | YouTube URL | Video File | Timestamp")
    print("\n📊 Sheet: 'Error Log' (Errors)")
    print("   Columns: Timestamp | Video ID | Topic | Error | Status")
    
    print("\nEnter your Google Spreadsheet ID")
    print("(Find it in the URL: docs.google.com/spreadsheets/d/[THIS_PART]/edit)")
    
    spreadsheet_id = input("\nSpreadsheet ID: ").strip()
    
    if spreadsheet_id:
        # Update config.json
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            config['google_sheets']['spreadsheet_id'] = spreadsheet_id
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n✓ Updated config.json with spreadsheet ID")


def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("Checking Dependencies")
    
    required_packages = [
        'google-api-python-client',
        'openai',
        'anthropic',
        'requests'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    print("\n✓ All required packages installed")
    return True


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print_header("Checking FFmpeg")
    
    import subprocess
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg installed: {version}")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ FFmpeg not found")
    print("\nFFmpeg is required for video processing.")
    print("Install instructions:")
    print("  macOS:   brew install ffmpeg")
    print("  Ubuntu:  sudo apt install ffmpeg")
    print("  Windows: Download from https://ffmpeg.org/download.html")
    return False


def run_test():
    """Run a basic test of the system"""
    print_header("Running System Test")
    
    print("This will test the basic functionality...")
    print("Note: This requires all credentials to be configured.")
    print("\nProceed with test? (y/n): ", end="")
    
    if input().lower() != 'y':
        print("Skipping test")
        return
    
    try:
        from auto_video_generator import AutoVideoGenerator
        
        generator = AutoVideoGenerator()
        print("✓ Successfully initialized AutoVideoGenerator")
        
        # More tests can be added here
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        print("\nMake sure all credentials are properly configured.")


def main():
    """Main setup function"""
    print("\n" + "=" * 60)
    print("  🎬 Automated Video Generator - Setup Wizard")
    print("=" * 60)
    
    print("\nThis wizard will help you set up the automated video system.")
    
    # Check current status
    print_header("Current Status")
    
    has_env = check_file_exists('.env', 'Environment file')
    has_google_creds = check_file_exists('google_credentials.json', 'Google credentials')
    has_youtube_creds = check_file_exists('client_secrets.json', 'YouTube credentials')
    has_config = check_file_exists('config.json', 'Configuration file')
    
    # Setup steps
    steps = [
        ("Install dependencies", check_dependencies),
        ("Check FFmpeg", check_ffmpeg),
        ("Create .env file", create_env_file),
        ("Setup Google Sheets", setup_google_sheets),
        ("Setup YouTube API", setup_youtube),
        ("Configure Spreadsheet", configure_spreadsheet),
        ("Run test", run_test)
    ]
    
    print("\n" + "=" * 60)
    print("Setup Steps:")
    for i, (step, _) in enumerate(steps, 1):
        print(f"  {i}. {step}")
    print("=" * 60)
    
    print("\nChoose an option:")
    print("  1. Run full setup wizard")
    print("  2. Run specific step")
    print("  3. Exit")
    
    choice = input("\nYour choice (1-3): ").strip()
    
    if choice == '1':
        for step_name, step_func in steps:
            try:
                step_func()
            except KeyboardInterrupt:
                print("\n\nSetup interrupted by user")
                sys.exit(0)
            except Exception as e:
                print(f"\n⚠️  Error in {step_name}: {str(e)}")
    
    elif choice == '2':
        print("\nSelect step:")
        for i, (step, _) in enumerate(steps, 1):
            print(f"  {i}. {step}")
        
        step_num = input("\nStep number: ").strip()
        try:
            step_idx = int(step_num) - 1
            if 0 <= step_idx < len(steps):
                steps[step_idx][1]()
            else:
                print("Invalid step number")
        except ValueError:
            print("Invalid input")
    
    print("\n" + "=" * 60)
    print("  Setup complete!")
    print("  Run: python auto_video_generator.py --help")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
