# 🎬 Automated Video Generator

**Drop a video idea in Google Sheets... and do nothing. In seconds, a full YouTube video gets made, uploaded, and logged without you touching a thing.**

## 📋 Overview

This system automates the entire video creation pipeline:

1. **Input**: Add video topics to Google Sheets
2. **Generation**: AI creates script, visuals, voiceover, and music
3. **Production**: Video is rendered and compiled
4. **Publishing**: Automatically uploads to YouTube
5. **Logging**: Results tracked back to Google Sheets

## ✨ Features

- 🤖 **AI-Powered Content**: Uses OpenAI/Anthropic for scripts and voiceovers
- 🎵 **Automatic Music**: Generates background music matched to video mood
- 🎬 **Video Composition**: Combines intro, scenes, voiceover, and music
- 📊 **Google Sheets Integration**: Simple input/output via spreadsheets
- 📺 **YouTube Upload**: Automatic publishing with metadata
- 🔄 **Error Handling**: Automatic retries and error logging
- 📝 **Comprehensive Logging**: Track every step of the process

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd automated-video-generator

# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg (required for video processing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### 2. Setup

Run the setup wizard:

```bash
python setup.py
```

Or configure manually:

#### A. API Keys

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

#### B. Google Sheets

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google Sheets API
3. Create a Service Account with Editor role
4. Download JSON credentials as `google_credentials.json`
5. Share your spreadsheet with the service account email

#### C. YouTube

1. In Google Cloud Console, enable YouTube Data API v3
2. Create OAuth 2.0 credentials (Desktop app)
3. Download as `client_secrets.json`

#### D. Configuration

Update `config.json` with your spreadsheet ID:

```json
{
  "google_sheets": {
    "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE"
  }
}
```

### 3. Spreadsheet Setup

Create a Google Sheet with these tabs:

**Sheet: "Video Ideas" (Input)**
| ID | Topic | Prompts | Status |
|----|-------|---------|--------|
| video_001 | 5 Tips for Better Sleep | Create a calm video about sleep hygiene | pending |

**Sheet: "Generated Videos" (Output)**
| ID | Topic | Status | YouTube URL | Video File | Timestamp |
|----|-------|--------|-------------|------------|-----------|

**Sheet: "Error Log" (Optional)**
| Timestamp | Video ID | Topic | Error | Status |
|-----------|----------|-------|-------|--------|

### 4. Run

```bash
# Process all pending videos once
python auto_video_generator.py --mode once

# Run continuously (checks every 60 seconds)
python auto_video_generator.py --mode continuous --interval 60

# Use custom config
python auto_video_generator.py --config my_config.json
```

## 📖 Detailed Documentation

### System Architecture

```
┌─────────────────────┐
│  Google Sheets      │
│  (Input)            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Auto Video         │
│  Generator          │
│                     │
│  ┌───────────────┐  │
│  │ Script Gen    │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ Music Gen     │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ Video Gen     │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ Voiceover     │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ Composition   │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  YouTube Upload     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Google Sheets      │
│  (Output + Logs)    │
└─────────────────────┘
```

### Workflow Steps

1. **Read Input**: Fetch pending videos from Google Sheets
2. **Generate Script**: AI creates video script with scenes and narration
3. **Create Music**: Generate background music matching video mood
4. **Generate Intro**: Create branded intro sequence
5. **Generate Scenes**: Create visual content for each scene
6. **Generate Voiceover**: Text-to-speech for narration
7. **Compose Video**: Combine all elements into final video
8. **Upload to YouTube**: Publish with metadata
9. **Log Results**: Update spreadsheet with video URL and status

### Configuration Options

#### `config.json`

```json
{
  "google_sheets": {
    "spreadsheet_id": "YOUR_ID",
    "input_sheet": "Video Ideas",
    "output_sheet": "Generated Videos",
    "credentials_path": "google_credentials.json"
  },
  "video_generation": {
    "ai_provider": "openai",  // or "anthropic"
    "video_duration": 60,
    "resolution": "1920x1080",
    "fps": 30,
    "use_ai_voiceover": true,
    "voice_model": "alloy"
  },
  "youtube": {
    "client_secrets_file": "client_secrets.json",
    "default_category": "22",  // People & Blogs
    "privacy_status": "private",  // or "public", "unlisted"
    "auto_publish": false
  },
  "error_handling": {
    "max_retries": 3,
    "retry_delay": 5,
    "log_errors_to_sheet": true
  }
}
```

### Error Handling

The system includes robust error handling:

- **Automatic Retries**: Failed videos retry up to 3 times
- **Error Logging**: All errors logged to "Error Log" sheet
- **Graceful Degradation**: Continues processing other videos if one fails
- **Status Tracking**: Each video's status updated in real-time

## 🎨 Customization

### Using Different AI Providers

```python
# In config.json, change ai_provider:
"ai_provider": "anthropic"  # Uses Claude for script generation

# Or use OpenAI:
"ai_provider": "openai"  # Uses GPT-4 for script generation
```

### Adding Custom Video Styles

Edit `video_generator.py`:

```python
def _generate_scenes(self, scenes):
    # Customize scene generation
    # Add custom filters, transitions, effects
    pass
```

### Custom Music Integration

```python
def _generate_music(self, mood, duration):
    # Integrate with music APIs:
    # - Mubert
    # - AIVA
    # - Soundraw
    # Or use local music library
    pass
```

## 🔧 Advanced Usage

### Batch Processing

```python
from auto_video_generator import AutoVideoGenerator

generator = AutoVideoGenerator('config.json')
generator.initialize_handlers()

# Process specific videos
video_ids = ['video_001', 'video_002']
for vid_id in video_ids:
    video_data = {'id': vid_id, 'topic': '...', 'prompts': '...'}
    result = generator.process_video_request(video_data)
    print(f"Processed: {result['youtube_url']}")
```

### Custom Integrations

```python
# Add webhooks
def on_video_complete(result):
    # Send notification
    # Update database
    # Trigger other workflows
    pass

# Add to auto_video_generator.py
generator.on_complete = on_video_complete
```

### API Extensions

The system can be extended with additional APIs:

- **Image Generation**: DALL-E, Midjourney, Stable Diffusion
- **Video Generation**: Runway ML, Pictory, Synthesia
- **Music**: ElevenLabs, Mubert, AIVA
- **Analytics**: YouTube Analytics API

## 📊 Monitoring

### Logs

All operations are logged to `video_automation.log`:

```bash
# Watch logs in real-time
tail -f video_automation.log

# Search for errors
grep ERROR video_automation.log
```

### Status Dashboard

Check Google Sheets for:
- Videos in progress
- Completed videos
- Error statistics
- Processing times

## 🐛 Troubleshooting

### Common Issues

**1. FFmpeg not found**
```bash
# Install FFmpeg first
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu
```

**2. Google Sheets permission denied**
```
- Share spreadsheet with service account email
- Check credentials file path
- Verify API is enabled
```

**3. YouTube upload fails**
```
- Check client_secrets.json is correct
- Run authentication flow
- Verify YouTube API quota
```

**4. Out of API credits**
```
- Check OpenAI/Anthropic usage
- Adjust retry settings
- Use longer delays
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance

Typical processing times:
- Script generation: 10-30 seconds
- Video generation: 2-5 minutes
- YouTube upload: 1-3 minutes
- **Total**: ~5-10 minutes per video

Optimization tips:
- Use video caching
- Batch process multiple videos
- Optimize video resolution
- Use faster AI models

## 🔒 Security

- **API Keys**: Store in `.env`, never commit to git
- **Credentials**: Keep JSON files secure
- **Access Control**: Limit service account permissions
- **Video Privacy**: Start with private uploads

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional AI provider integrations
- Enhanced video effects
- Better error recovery
- UI dashboard
- Analytics integration

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review logs in `video_automation.log`
3. Check Google Cloud Console for API errors
4. Verify all credentials are correctly configured

## 🎯 Roadmap

- [ ] Web dashboard for monitoring
- [ ] Multiple language support
- [ ] Advanced video templates
- [ ] Social media cross-posting
- [ ] Analytics and insights
- [ ] Thumbnail generation
- [ ] SEO optimization
- [ ] Scheduled publishing

## 🌟 Examples

### Example 1: Educational Content
```
Topic: "Python Basics: Variables and Data Types"
Prompts: "Create an educational video with code examples and clear explanations"
Result: Professional tutorial with code visualization
```

### Example 2: Product Reviews
```
Topic: "Top 5 Smartphones of 2024"
Prompts: "Upbeat comparison video with product images and key specs"
Result: Engaging review with product comparisons
```

### Example 3: News Summary
```
Topic: "This Week in Tech: Major AI Developments"
Prompts: "Professional news format with recent tech news"
Result: News-style video with current events
```

---

**Made with ❤️ for automating video creation**
