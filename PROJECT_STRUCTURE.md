# 📁 Project Structure

```
automated-video-generator/
│
├── 📄 auto_video_generator.py      # Main orchestration script
├── 📄 sheets_handler.py             # Google Sheets integration
├── 📄 video_generator.py            # Video creation logic
├── 📄 youtube_uploader.py           # YouTube upload handler
│
├── 📄 setup.py                      # Interactive setup wizard
├── 📄 examples.py                   # Usage examples
├── 📄 quickstart.sh                 # Quick start script
│
├── 📄 config.json                   # Configuration file
├── 📄 .env.template                 # API keys template
├── 📄 requirements.txt              # Python dependencies
├── 📄 .gitignore                    # Git ignore rules
│
├── 📄 README.md                     # Full documentation
├── 📄 PROJECT_STRUCTURE.md          # This file
│
├── 🔐 .env                          # API keys (create from template)
├── 🔐 google_credentials.json       # Google service account (you provide)
├── 🔐 client_secrets.json           # YouTube OAuth (you provide)
│
└── 📁 output_videos/                # Generated videos (auto-created)
    ├── video_*.mp4
    ├── music_*.mp3
    └── intro_*.mp4
```

## Core Components

### 1. Main Orchestrator (`auto_video_generator.py`)
- Entry point for the system
- Coordinates all components
- Handles workflow execution
- Manages error handling and retries

**Key Classes:**
- `AutoVideoGenerator`: Main orchestrator class

**Key Methods:**
- `run_once()`: Process all pending videos once
- `run_continuous()`: Continuous monitoring mode
- `process_video_request()`: Process single video
- `handle_error()`: Error handling with retries

### 2. Google Sheets Handler (`sheets_handler.py`)
- Reads video requests from spreadsheet
- Writes results back to spreadsheet
- Manages error logging

**Key Classes:**
- `GoogleSheetsHandler`: Spreadsheet operations

**Key Methods:**
- `get_pending_videos()`: Fetch videos to process
- `append_to_sheet()`: Write results
- `update_row_status()`: Update video status

### 3. Video Generator (`video_generator.py`)
- Generates scripts using AI
- Creates video scenes
- Generates voiceover
- Produces background music
- Combines all elements

**Key Classes:**
- `VideoGenerator`: Video creation logic

**Key Methods:**
- `generate_full_video()`: Complete video generation
- `_generate_script()`: AI script generation
- `_generate_scenes()`: Scene creation
- `_generate_voiceover()`: Text-to-speech
- `_generate_music()`: Background music
- `_combine_video_elements()`: Final composition

### 4. YouTube Uploader (`youtube_uploader.py`)
- Authenticates with YouTube
- Uploads videos
- Manages video metadata
- Handles privacy settings

**Key Classes:**
- `YouTubeUploader`: YouTube operations

**Key Methods:**
- `upload_video()`: Upload to YouTube
- `update_video()`: Update video metadata
- `get_video_status()`: Check upload status

## Setup and Configuration Files

### `setup.py`
Interactive wizard that guides through:
- API key configuration
- Google Sheets setup
- YouTube API setup
- Spreadsheet configuration
- Dependency checking

### `config.json`
Central configuration for:
- Spreadsheet IDs and sheet names
- Video generation settings
- YouTube upload settings
- Error handling parameters

### `.env`
Environment variables for:
- API keys (OpenAI, Anthropic, etc.)
- Sensitive credentials
- Optional service keys

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Google Sheets Input                                      │
│    User adds video topics and prompts                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Fetch Pending Videos                                     │
│    sheets_handler.get_pending_videos()                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Generate Script                                          │
│    video_generator._generate_script()                       │
│    - Uses AI (OpenAI/Anthropic)                            │
│    - Creates narration and scene descriptions               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Create Video Elements                                    │
│    - Generate scenes: _generate_scenes()                    │
│    - Generate music: _generate_music()                      │
│    - Generate voiceover: _generate_voiceover()             │
│    - Create intro: _generate_intro()                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Combine Elements                                         │
│    video_generator._combine_video_elements()                │
│    - Uses FFmpeg                                            │
│    - Merges video, audio, music                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Upload to YouTube                                        │
│    youtube_uploader.upload_video()                          │
│    - Authenticates with OAuth                               │
│    - Uploads with metadata                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Log Results                                              │
│    sheets_handler.append_to_sheet()                         │
│    - Updates "Generated Videos" sheet                       │
│    - Logs errors if any                                     │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────┐
│ Process Video   │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ Error? │──No──▶ Success ──▶ Log to Sheets ──▶ Done
    └───┬────┘
        │
       Yes
        │
        ▼
┌───────────────────┐
│ Retry < Max?      │
└───────┬───────────┘
        │
        ├──Yes──▶ Wait ──▶ Retry Process
        │
       No
        │
        ▼
┌───────────────────┐
│ Log Error         │
│ Mark as Failed    │
└───────────────────┘
```

## Data Flow

### Input (Google Sheets)
```
Video Ideas Sheet:
┌────┬─────────────────────────┬────────────────────┬─────────┐
│ ID │ Topic                   │ Prompts            │ Status  │
├────┼─────────────────────────┼────────────────────┼─────────┤
│ 01 │ 5 Tips for Better Sleep │ Calm, informative  │ pending │
│ 02 │ AI in 2025              │ Futuristic visuals │ pending │
└────┴─────────────────────────┴────────────────────┴─────────┘
```

### Output (Google Sheets)
```
Generated Videos Sheet:
┌────┬──────────┬───────────┬──────────────────────┬───────────────────┐
│ ID │ Topic    │ Status    │ YouTube URL          │ Timestamp         │
├────┼──────────┼───────────┼──────────────────────┼───────────────────┤
│ 01 │ Sleep... │ completed │ youtube.com/watch... │ 2024-01-15 10:30  │
│ 02 │ AI...    │ completed │ youtube.com/watch... │ 2024-01-15 10:45  │
└────┴──────────┴───────────┴──────────────────────┴───────────────────┘
```

## Dependencies

### Python Packages
- **google-api-python-client**: Google Sheets & YouTube APIs
- **openai**: GPT-4 for script generation
- **anthropic**: Claude for alternative AI
- **moviepy**: Video editing
- **opencv-python**: Video processing
- **requests**: HTTP requests

### System Requirements
- **FFmpeg**: Video/audio processing
- **Python 3.8+**: Runtime environment
- **Internet**: API access

## Extension Points

The system is designed to be extensible:

### 1. Add New AI Providers
```python
# In video_generator.py
def _generate_script(self, topic, prompts):
    if self.ai_provider == 'custom':
        # Add your custom AI logic
        pass
```

### 2. Custom Video Styles
```python
# In video_generator.py
def _generate_scenes(self, scenes):
    # Add custom scene generation
    # Integrate with image/video APIs
    pass
```

### 3. Additional Output Formats
```python
# In youtube_uploader.py
def upload_to_platform(self, platform, video_path):
    if platform == 'tiktok':
        # Add TikTok upload
        pass
```

### 4. Webhooks and Notifications
```python
# In auto_video_generator.py
def on_video_complete(self, result):
    # Send to Discord, Slack, etc.
    pass
```

## Security Considerations

### Credentials Storage
- ✅ `.env` for API keys
- ✅ Separate JSON files for OAuth
- ✅ `.gitignore` to prevent commits
- ❌ Never hardcode credentials

### API Access
- ✅ Use service accounts for Sheets
- ✅ OAuth2 for YouTube
- ✅ Scope limitation
- ❌ Don't share credentials

### File Permissions
- Credentials: 600 (read/write owner only)
- Scripts: 755 (executable)
- Config: 644 (read for all)

## Monitoring and Logging

### Log Files
- `video_automation.log`: All operations
- Console output: Real-time progress
- Google Sheets: Final results

### What's Logged
- Video processing start/complete
- API calls and responses
- Errors and stack traces
- Upload status
- Performance metrics

## Performance Optimization

### Bottlenecks
1. **AI Generation**: 10-30s per script
2. **Video Rendering**: 2-5 min per video
3. **YouTube Upload**: 1-3 min per video

### Optimization Strategies
- Batch processing
- Caching generated assets
- Parallel processing
- Lower resolution for testing
- Faster AI models

## Testing

### Manual Testing
```bash
# Test single video
python examples.py

# Test with custom data
python auto_video_generator.py --mode once
```

### Component Testing
```bash
# Test sheets connection
python -c "from sheets_handler import *; test_connection()"

# Test YouTube upload
python youtube_uploader.py test_video.mp4

# Test video generation
python video_generator.py --test
```

## Troubleshooting

Common issues and solutions documented in:
- `README.md` - Troubleshooting section
- `video_automation.log` - Detailed logs
- Error messages - Self-explanatory

## Future Enhancements

Potential additions:
- [ ] Web dashboard
- [ ] Real-time progress tracking
- [ ] Multi-language support
- [ ] Advanced video effects
- [ ] Social media cross-posting
- [ ] Analytics integration
- [ ] Thumbnail generation
- [ ] A/B testing

---

For detailed usage instructions, see `README.md`
For setup help, run `python setup.py`
For examples, run `python examples.py`
