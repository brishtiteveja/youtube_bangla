# 🇧🇩 YouTube Transcript Collector

A clean, modular Python application for collecting YouTube video transcripts with a focus on Bangladeshi content.

## 📁 Project Structure

```
youtube_transcript_collector/
├── src/                          # Source code modules
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── youtube_api.py           # YouTube Data API client
│   ├── transcript_api.py        # Transcript fetching & formatting
│   └── channel_database.py      # BD channels database manager
├── data/                         # Data files
│   └── bangladeshi_channels.json # 1000 BD channels database
├── output/                       # Output directory (auto-created)
├── docs/                         # Documentation (auto-created)
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── run.sh                        # Quick start script (uses uv)
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Install uv** (Modern Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Clone or navigate to project**:
```bash
cd youtube_transcript_collector
```

### Run the Application

**Option 1: Using run script** (Recommended)
```bash
./run.sh
```

**Option 2: Manual commands**
```bash
# Install dependencies
uv pip install -r requirements.txt

# Run the app
uv run streamlit run app.py
```

The app will open at: **http://localhost:8501**

## ✨ Features

### 🎯 Core Features
- **1000 Bangladeshi Channels** - Pre-loaded ranked database
- **Default Channel** - Pinaki Bhattacharya loads instantly
- **Multi-language** - Bangla (বাংলা), English, Hindi transcripts
- **Search Methods** - BD database, global search, or direct URL
- **Download Formats** - JSON (structured) or TXT (readable)

### 🏗️ Architecture Features
- **Modular Design** - Clean class hierarchy
- **Separation of Concerns** - API, Database, Formatting separated
- **Configuration Management** - Centralized config
- **Caching** - Optimized performance with Streamlit caching
- **Type Hints** - Fully typed for better IDE support

## 📚 Module Documentation

### 1. `config.py` - Configuration
Centralized configuration for the entire application.

```python
from config import Config

# Access settings
api_key = Config.YOUTUBE_API_KEY
default_channel = Config.DEFAULT_CHANNEL
languages = Config.DEFAULT_LANGUAGES
```

### 2. `youtube_api.py` - YouTube API Client
Handles all YouTube Data API v3 operations.

```python
from youtube_api import YouTubeAPIClient, ChannelManager

# Initialize client
api_client = YouTubeAPIClient(api_key)

# Search channels
channels = api_client.search_channels("BBC News", max_results=10)

# Get channel info
channel = api_client.get_channel_info("channel_id")

# Get videos
videos = api_client.get_channel_videos("channel_id", max_results=50)

# High-level operations
manager = ChannelManager(api_client)
channel = manager.get_channel_by_url("https://youtube.com/@ChannelName")
```

**Classes:**
- `YouTubeAPIClient` - Low-level API client
- `ChannelManager` - High-level channel operations

### 3. `transcript_api.py` - Transcript Operations
Handles transcript fetching and formatting.

```python
from transcript_api import TranscriptProcessor

# Initialize processor
processor = TranscriptProcessor()

# Get and format transcript
result = processor.get_and_format(
    video_id="VIDEO_ID",
    video_title="Video Title",
    languages=['bn', 'en'],
    format_type='timestamped'  # or 'plain'
)

if result['success']:
    print(result['formatted_text'])
    print(result['metadata'])
```

**Classes:**
- `TranscriptFetcher` - Fetches transcripts from YouTube
- `TranscriptFormatter` - Formats transcripts (timestamped/plain/JSON)
- `TranscriptProcessor` - High-level combined operations

### 4. `channel_database.py` - Channel Database
Manages the Bangladeshi channels database.

```python
from channel_database import ChannelDatabase

# Initialize database
db = ChannelDatabase()

# Search channels
results = db.search_channels("Jamuna", limit=10)

# Get top channels
top_50 = db.get_top_channels(50)

# Get by rank
channel = db.get_channel_by_rank(1)  # #1 channel

# Get stats
stats = db.get_stats()
```

**Methods:**
- `search_channels()` - Search by name
- `get_top_channels()` - Get top N by rank
- `get_channel_by_rank()` - Get specific rank
- `format_for_display()` - Format for UI display

## 🎨 Usage Examples

### Example 1: Get Transcript for Specific Video

```python
from src.transcript_api import TranscriptProcessor

processor = TranscriptProcessor()

result = processor.get_and_format(
    video_id="m4ri2oiiKik",
    video_title="Political Commentary",
    languages=['bn'],  # Bangla
    format_type='timestamped'
)

if result['success']:
    # Save to file
    with open('transcript.txt', 'w', encoding='utf-8') as f:
        f.write(result['formatted_text'])

    # Access metadata
    print(f"Language: {result['metadata']['language_code']}")
    print(f"Entries: {result['metadata']['entry_count']}")
```

### Example 2: Get All Videos from Channel

```python
from src.youtube_api import YouTubeAPIClient
from src.config import Config

api_client = YouTubeAPIClient(Config.YOUTUBE_API_KEY)

# Search for channel
channels = api_client.search_channels("Pinaki Bhattacharya")
channel_id = channels[0]['channel_id']

# Get channel videos
videos = api_client.get_channel_videos(
    channel_id,
    max_results=100,
    show_progress=False
)

for video in videos:
    print(f"{video['title']} - {video['video_id']}")
```

### Example 3: Batch Process Transcripts

```python
from src.youtube_api import YouTubeAPIClient
from src.transcript_api import TranscriptProcessor
from src.config import Config
import json

api_client = YouTubeAPIClient(Config.YOUTUBE_API_KEY)
processor = TranscriptProcessor()

# Get channel videos
videos = api_client.get_channel_videos("CHANNEL_ID", max_results=50)

# Process each video
for video in videos:
    result = processor.get_and_format(
        video['video_id'],
        video['title'],
        languages=['bn']
    )

    if result['success']:
        # Save JSON
        filename = f"output/{video['video_id']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result['json_data'], f, ensure_ascii=False, indent=2)
```

### Example 4: Use Channel Database

```python
from src.channel_database import ChannelDatabase
from src.youtube_api import YouTubeAPIClient, ChannelManager
from src.config import Config

db = ChannelDatabase()
api_client = YouTubeAPIClient(Config.YOUTUBE_API_KEY)
manager = ChannelManager(api_client)

# Search BD channels
news_channels = db.search_channels("news", limit=10)

# Load each channel
for bd_channel in news_channels:
    print(f"Loading: {bd_channel['name']}")

    # Search YouTube for this channel
    result = manager.search_and_select(bd_channel['name'])

    if result:
        print(f"  Found: {result['title']}")
        print(f"  Videos: {result['video_count']}")
```

## 🔧 Configuration

Edit `src/config.py` to customize:

```python
class Config:
    # API Key (Get from Google Cloud Console)
    YOUTUBE_API_KEY = 'your-api-key-here'

    # Default Settings
    DEFAULT_CHANNEL = "Pinaki Bhattacharya"
    DEFAULT_VIDEO_COUNT = 50
    MAX_VIDEO_COUNT = 200

    # Languages
    DEFAULT_LANGUAGES = ['bn', 'en', 'hi']
```

## 📊 Database

The `bangladeshi_channels.json` contains 1000 Bangladeshi YouTube channels:

```json
{
  "channels": [
    {
      "rank": 1,
      "name": "Jamuna TV"
    },
    {
      "rank": 2,
      "name": "Ekattor TV"
    }
    ...
  ]
}
```

## 🛠️ Development

### Adding New Features

1. **Add new API endpoint**:
   - Edit `src/youtube_api.py`
   - Add method to `YouTubeAPIClient` or `ChannelManager`

2. **Add new transcript format**:
   - Edit `src/transcript_api.py`
   - Add method to `TranscriptFormatter`

3. **Add new configuration**:
   - Edit `src/config.py`
   - Add to `Config` class

### Testing Individual Modules

```python
# Test YouTube API
from src.youtube_api import YouTubeAPIClient
from src.config import Config

api = YouTubeAPIClient(Config.YOUTUBE_API_KEY)
channels = api.search_channels("test")
print(channels)

# Test Transcript API
from src.transcript_api import TranscriptFetcher

fetcher = TranscriptFetcher()
result = fetcher.get_transcript("VIDEO_ID", languages=['bn'])
print(result)

# Test Database
from src.channel_database import ChannelDatabase

db = ChannelDatabase()
print(db.get_stats())
```

## 📝 API Keys

### Get Your Own YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create credentials (API Key)
5. Update `src/config.py`:
   ```python
   YOUTUBE_API_KEY = 'your-api-key-here'
   ```

**Free Tier Limits:**
- 10,000 quota units per day
- ~100 video list operations per day
- ~10,000 searches per day

## 🌍 Language Codes

Supported transcript languages:

| Language | Code | Example Channel |
|----------|------|-----------------|
| Bangla | `bn` | Pinaki Bhattacharya, Jamuna TV |
| English | `en` | BBC News, CNN |
| Hindi | `hi` | Zee News, Aaj Tak |
| Auto | `auto` | Tries all available languages |

## 🔒 Proxy Setup (Recommended)

To avoid YouTube IP blocking when fetching transcripts, use **Webshare proxies**:

### Quick Setup
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Add your Webshare credentials to .env
nano .env

# 3. Set USE_PROXY=true and add credentials
# 4. Run the app normally
```

**Get Webshare proxies**: https://www.webshare.io/ (10 free proxies in trial)

📖 **Full guide**: See [docs/PROXY_SETUP.md](docs/PROXY_SETUP.md) for detailed instructions

## 🐛 Troubleshooting

### Issue: "IP blocked" or "Could not retrieve transcript"
**Solution**: YouTube is blocking your IP. Use proxies:
- See [docs/PROXY_SETUP.md](docs/PROXY_SETUP.md) for Webshare setup
- Or wait several hours before retrying
- Use a different network connection

### Issue: "No transcript found"
**Solution**: Not all videos have transcripts. Try:
- Different language codes
- Auto-detect mode
- Check if video is recent (transcripts may take time)

### Issue: "API quota exceeded"
**Solution**:
- Wait 24 hours for reset
- Get your own API key
- Reduce number of requests

### Issue: "Module not found"
**Solution**:
```bash
# Reinstall dependencies
uv pip install -r requirements.txt

# Or use pip
pip install -r requirements.txt
```

### Issue: "uv command not found"
**Solution**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use regular pip
pip install -r requirements.txt
python -m streamlit run app.py
```

## 📄 License

MIT License - Free to use and modify

## 🙏 Credits

- **Streamlit** - Web framework
- **youtube-transcript-api** - Transcript fetching
- **YouTube Data API v3** - Channel/video metadata

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review module documentation
3. Examine example code
4. Test individual modules

---

**Made with ❤️ for Bangladesh** 🇧🇩

Version: 1.0.0
