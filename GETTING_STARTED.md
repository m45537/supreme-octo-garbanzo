# 🚀 Getting Started with Automated Video Generator

Welcome! This guide will help you set up your automated video generation system in just a few minutes.

## 📦 What You're Getting

This system automatically:
1. Reads video topics from Google Sheets
2. Generates scripts using AI (OpenAI or Anthropic)
3. Creates videos with voiceover and music
4. Uploads to YouTube
5. Logs everything back to Google Sheets

**Result**: Drop a video idea in a spreadsheet → Get a published YouTube video without touching anything!

## ⚡ Quick Start (5 Minutes)

### Step 1: Prerequisites

You need:
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **FFmpeg** ([Download](https://ffmpeg.org/download.html))
- **Git** (optional, for cloning)

### Step 2: Install

```bash
# Option A: Clone repository (if using Git)
git clone <repository-url>
cd automated-video-generator

# Option B: Extract downloaded ZIP
unzip automated-video-generator.zip
cd automated-video-generator

# Run quick start script
chmod +x quickstart.sh
./quickstart.sh
```

The script will:
- Check dependencies
- Create virtual environment
- Install Python packages
- Guide you through configuration

### Step 3: Configure API Keys

Create a `.env` file (copy from `.env.template`):

```bash
cp .env.template .env
nano .env  # or use any text editor
```

Add your keys:
```env
OPENAI_API_KEY=sk-...your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-...your-key-here
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

### Step 4: Set Up Google Sheets

#### A. Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Google Sheets API**
4. Create **Service Account**:
   - IAM & Admin → Service Accounts
   - Create Service Account
   - Grant "Editor" role
   - Create JSON key
5. Save as `google_credentials.json`

#### B. Create Your Spreadsheet
1. Create a new Google Sheet
2. Add three sheets:
   - **"Video Ideas"** (input)
   - **"Generated Videos"** (output)
   - **"Error Log"** (errors)

3. Set up columns:

**Video Ideas:**
| ID | Topic | Prompts | Status |
|----|-------|---------|--------|
| video_001 | 5 Tips for Better Sleep | Calm, informative video | pending |

**Generated Videos:**
| ID | Topic | Status | YouTube URL | Video File | Timestamp |
|----|-------|--------|-------------|------------|-----------|

4. Share spreadsheet with service account email (found in `google_credentials.json`)
5. Copy spreadsheet ID from URL: `docs.google.com/spreadsheets/d/[THIS_IS_THE_ID]/edit`

#### C. Update Config
Edit `config.json`:
```json
{
  "google_sheets": {
    "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE"
  }
}
```

### Step 5: Set Up YouTube

#### A. Get OAuth Credentials
1. Same Google Cloud project as above
2. Enable **YouTube Data API v3**
3. Create **OAuth 2.0 Client ID**:
   - APIs & Services → Credentials
   - Create Credentials → OAuth 2.0 Client ID
   - Application type: **Desktop app**
   - Download JSON
4. Save as `client_secrets.json`

#### B. First-Time Authentication
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run authentication
python youtube_uploader.py
```

This will:
- Open browser for Google login
- Save authentication token
- You only need to do this once!

### Step 6: Run Your First Video

```bash
# Process all pending videos in your sheet
python auto_video_generator.py --mode once
```

Watch the magic happen! ✨

The system will:
1. Read video topics from your sheet
2. Generate scripts with AI
3. Create videos with voiceover
4. Upload to YouTube
5. Update your sheet with results

## 📊 Using the System

### Add New Videos

Just add rows to your "Video Ideas" sheet:

| ID | Topic | Prompts | Status |
|----|-------|---------|--------|
| video_001 | Why Dogs Are Great | Upbeat, fun video with dog footage | pending |
| video_002 | How to Make Coffee | Educational, morning vibes | pending |

Then run:
```bash
python auto_video_generator.py --mode once
```

### Continuous Mode

Want it to run automatically? Use continuous mode:

```bash
python auto_video_generator.py --mode continuous --interval 60
```

This checks for new videos every 60 seconds and processes them automatically.

**Pro Tip**: Run this in a screen/tmux session or as a systemd service for 24/7 operation!

## 🎨 Customization

### Change AI Provider

Edit `config.json`:
```json
{
  "video_generation": {
    "ai_provider": "anthropic"  // or "openai"
  }
}
```

### Video Settings

```json
{
  "video_generation": {
    "video_duration": 45,      // seconds
    "resolution": "1920x1080", // or "1280x720"
    "fps": 30
  }
}
```

### YouTube Settings

```json
{
  "youtube": {
    "default_category": "27",     // Education
    "privacy_status": "unlisted"  // or "private", "public"
  }
}
```

**YouTube Categories:**
- 22: People & Blogs
- 27: Education
- 24: Entertainment
- 25: News & Politics

## 🔍 Monitoring

### Check Logs
```bash
# View real-time logs
tail -f video_automation.log

# Search for errors
grep ERROR video_automation.log
```

### Check Spreadsheet
Your "Generated Videos" sheet shows:
- ✅ Completed videos with YouTube URLs
- ⏳ Videos in progress
- ❌ Failed videos with error messages

## 🎯 Usage Examples

### Example 1: Educational Content
```
Topic: "Introduction to Python Programming"
Prompts: "Beginner-friendly tutorial with code examples and clear explanations"
```

### Example 2: Product Review
```
Topic: "Best Budget Headphones 2024"
Prompts: "Comparison video with product images and pros/cons"
```

### Example 3: Quick Tips
```
Topic: "5 Productivity Hacks for Remote Work"
Prompts: "Fast-paced, energetic video with modern graphics"
```

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "FFmpeg not found"
```bash
# Install FFmpeg
# macOS:
brew install ffmpeg

# Ubuntu:
sudo apt install ffmpeg
```

### "Permission denied" (Google Sheets)
1. Check service account email in `google_credentials.json`
2. Share spreadsheet with that email address
3. Verify API is enabled in Google Cloud Console

### "YouTube upload failed"
1. Check `client_secrets.json` is correct
2. Re-run authentication: `python youtube_uploader.py`
3. Check YouTube API quota in Cloud Console

### Videos taking too long?
1. Lower resolution in config: `"resolution": "1280x720"`
2. Reduce duration: `"video_duration": 30`
3. Use faster AI models

## 📚 Additional Resources

### Documentation
- **README.md**: Complete documentation
- **PROJECT_STRUCTURE.md**: System architecture
- **examples.py**: Code examples

### Interactive Tools
```bash
# Setup wizard
python setup.py

# Usage examples
python examples.py
```

### Help Commands
```bash
# Get help
python auto_video_generator.py --help

# Check configuration
python -c "import json; print(json.load(open('config.json')))"
```

## 🚀 Production Deployment

### Run as Background Service

#### Linux (systemd):
```bash
# Create service file
sudo nano /etc/systemd/system/video-automation.service
```

```ini
[Unit]
Description=Automated Video Generator
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/automated-video-generator
ExecStart=/path/to/venv/bin/python auto_video_generator.py --mode continuous
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable video-automation
sudo systemctl start video-automation

# Check status
sudo systemctl status video-automation
```

#### macOS (launchd):
```bash
# Create plist file
nano ~/Library/LaunchAgents/com.video-automation.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.video-automation</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/auto_video_generator.py</string>
        <string>--mode</string>
        <string>continuous</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

```bash
# Load service
launchctl load ~/Library/LaunchAgents/com.video-automation.plist
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Copy project
WORKDIR /app
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Run
CMD ["python", "auto_video_generator.py", "--mode", "continuous"]
```

```bash
# Build and run
docker build -t video-automation .
docker run -d --name video-gen video-automation
```

## 💡 Pro Tips

1. **Start Small**: Test with short videos (30s) first
2. **Use Private**: Set privacy to "private" until you verify quality
3. **Monitor Logs**: Check logs regularly for errors
4. **Backup Config**: Keep copies of your credentials
5. **Test APIs**: Verify API keys work before bulk processing
6. **Set Limits**: Be mindful of API rate limits
7. **Review First**: Check the first few videos manually

## 🎓 Next Steps

Once you're comfortable:
1. Experiment with different video styles
2. Try batch processing multiple videos
3. Set up continuous monitoring
4. Customize video templates
5. Add more AI integrations
6. Build a content calendar

## 🆘 Getting Help

### Check These First:
1. Log files: `video_automation.log`
2. Error sheet in Google Sheets
3. README.md troubleshooting section
4. Examples: `python examples.py`

### Common Fixes:
- **Restart**: Often solves temporary issues
- **Re-authenticate**: YouTube token expires
- **Check quotas**: APIs have daily limits
- **Update dependencies**: `pip install --upgrade -r requirements.txt`

## 🎉 Success!

If you've made it here and created your first video, congratulations! 🎊

You now have a fully automated video creation pipeline. Just drop ideas in a spreadsheet and watch them become YouTube videos!

---

**Questions?** Review the documentation in README.md or run `python setup.py` for interactive help.

**Ready to scale?** Check out continuous mode and production deployment options above!
