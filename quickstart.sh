#!/bin/bash

# Quick Start Script for Automated Video Generator
# This script helps you get started quickly

set -e  # Exit on error

echo ""
echo "=========================================="
echo "  🎬 Automated Video Generator"
echo "  Quick Start Setup"
echo "=========================================="
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

# Check FFmpeg
echo ""
echo "Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed"
    echo ""
    echo "FFmpeg is required for video processing."
    echo "Install it with:"
    echo "  macOS:   brew install ffmpeg"
    echo "  Ubuntu:  sudo apt install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
    echo ""
    read -p "Continue without FFmpeg? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
    echo "✓ FFmpeg $FFMPEG_VERSION found"
fi

# Create virtual environment
echo ""
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
echo "This may take a few minutes..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check for credentials
echo ""
echo "Checking credentials..."

# .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "Creating from template..."
    cp .env.template .env
    echo "✓ Created .env - Please add your API keys"
    NEED_CONFIG=true
else
    echo "✓ .env file exists"
fi

# Google credentials
if [ ! -f "google_credentials.json" ]; then
    echo "⚠️  google_credentials.json not found"
    NEED_CONFIG=true
else
    echo "✓ Google credentials found"
fi

# YouTube credentials
if [ ! -f "client_secrets.json" ]; then
    echo "⚠️  client_secrets.json not found"
    NEED_CONFIG=true
else
    echo "✓ YouTube credentials found"
fi

# config.json
if [ ! -f "config.json" ]; then
    echo "❌ config.json not found"
    exit 1
else
    # Check if spreadsheet ID is set
    if grep -q "YOUR_SPREADSHEET_ID_HERE" config.json; then
        echo "⚠️  Spreadsheet ID not configured in config.json"
        NEED_CONFIG=true
    else
        echo "✓ config.json configured"
    fi
fi

# Summary
echo ""
echo "=========================================="
echo "  Setup Summary"
echo "=========================================="
echo ""

if [ "$NEED_CONFIG" = true ]; then
    echo "⚠️  Configuration needed!"
    echo ""
    echo "Next steps:"
    echo "  1. Add API keys to .env file"
    echo "  2. Add google_credentials.json (Google Sheets API)"
    echo "  3. Add client_secrets.json (YouTube API)"
    echo "  4. Update spreadsheet_id in config.json"
    echo ""
    echo "Run setup wizard for help:"
    echo "  python setup.py"
    echo ""
else
    echo "✓ All configuration files present!"
    echo ""
    echo "You're ready to start!"
    echo ""
    echo "Quick commands:"
    echo "  python auto_video_generator.py --mode once"
    echo "  python auto_video_generator.py --mode continuous"
    echo "  python examples.py"
    echo ""
fi

echo "Documentation:"
echo "  README.md - Full documentation"
echo "  examples.py - Usage examples"
echo "  setup.py - Setup wizard"
echo ""
echo "=========================================="
echo ""

# Ask to run setup wizard
if [ "$NEED_CONFIG" = true ]; then
    read -p "Run setup wizard now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python setup.py
    fi
fi
