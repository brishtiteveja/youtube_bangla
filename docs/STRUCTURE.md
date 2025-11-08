# 📂 Project Structure

## Complete File Tree

```
youtube/
└── youtube_transcript_collector/          # Main Project Directory
    │
    ├── app.py                             # 🚀 Main Streamlit Application
    ├── run.sh                             # ⚡ Quick Launch Script (uses uv)
    ├── requirements.txt                   # 📦 Python Dependencies
    │
    ├── README.md                          # 📖 Main Documentation
    ├── PROJECT_SUMMARY.md                 # 📋 Project Overview
    ├── STRUCTURE.md                       # 📂 This File
    │
    ├── src/                               # 💻 Source Code Modules
    │   ├── __init__.py                    # Package initialization
    │   ├── config.py                      # ⚙️  Configuration management
    │   ├── youtube_api.py                 # 📺 YouTube API client
    │   ├── transcript_api.py              # 📝 Transcript operations
    │   └── channel_database.py            # 🗄️  BD channels database
    │
    ├── data/                              # 💾 Data Files
    │   └── bangladeshi_channels.json      # 1000 BD channels ranked
    │
    ├── docs/                              # 📚 Documentation
    │   ├── QUICKSTART.md                  # Quick start guide
    │   ├── ARCHITECTURE.md                # Technical architecture
    │   └── examples.py                    # Working code examples
    │
    └── output/                            # 📁 Output Directory (auto-created)
        └── (transcript files saved here)
```

## File Descriptions

### Root Level

| File | Description | Use |
|------|-------------|-----|
| `app.py` | Main Streamlit web application | Run with `uv run streamlit run app.py` |
| `run.sh` | Quick launch script | Run with `./run.sh` |
| `requirements.txt` | Python dependencies | Install with `uv pip install -r requirements.txt` |
| `README.md` | Comprehensive documentation | Read first for full overview |
| `PROJECT_SUMMARY.md` | Quick project overview | Quick reference guide |
| `STRUCTURE.md` | This file | Project structure reference |

### src/ - Source Code

| Module | Classes | Purpose |
|--------|---------|---------|
| `config.py` | `Config` | Centralized configuration |
| `youtube_api.py` | `YouTubeAPIClient`<br>`ChannelManager` | YouTube Data API operations |
| `transcript_api.py` | `TranscriptFetcher`<br>`TranscriptFormatter`<br>`TranscriptProcessor` | Transcript fetching and formatting |
| `channel_database.py` | `ChannelDatabase` | BD channels database management |
| `__init__.py` | - | Package exports |

### data/ - Data Files

| File | Content | Size |
|------|---------|------|
| `bangladeshi_channels.json` | 1000 Bangladeshi YouTube channels with ranks | ~45 KB |

### docs/ - Documentation

| File | Content | For |
|------|---------|-----|
| `QUICKSTART.md` | Quick 3-step start guide | New users |
| `ARCHITECTURE.md` | Technical architecture docs | Developers |
| `examples.py` | 6 working code examples | Learning |

## Module Relationships

```
┌─────────────────────────────────────────────┐
│                  app.py                     │
│            (Streamlit UI)                   │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
┌───────────┐ ┌──────────┐ ┌────────────┐
│  youtube  │ │transcript│ │  channel   │
│    api    │ │   api    │ │  database  │
└───────────┘ └──────────┘ └────────────┘
        │           │           │
        └───────────┼───────────┘
                    ↓
            ┌──────────────┐
            │    config    │
            └──────────────┘
```

## Class Hierarchy

```
Config (Static)
    │
    ├─→ YouTubeAPIClient
    │       └─→ ChannelManager
    │
    ├─→ TranscriptFetcher
    │       └─→ TranscriptFormatter
    │               └─→ TranscriptProcessor
    │
    └─→ ChannelDatabase
```

## Data Flow

### User Action → Transcript Download

```
1. User clicks "Get Transcript"
         ↓
2. app.py (UI Layer)
         ↓
3. TranscriptProcessor.get_and_format()
         ↓
4. TranscriptFetcher.get_transcript()
         ↓
5. youtube-transcript-api (External)
         ↓
6. TranscriptFormatter.format_*()
         ↓
7. Return formatted text + JSON
         ↓
8. User downloads file
```

## Key Paths

### Configuration
```python
# In any module
from config import Config

api_key = Config.YOUTUBE_API_KEY
default_channel = Config.DEFAULT_CHANNEL
output_dir = Config.OUTPUT_DIR
```

### Import Modules
```python
# From external scripts
import sys
sys.path.insert(0, 'src')

from youtube_api import YouTubeAPIClient
from transcript_api import TranscriptProcessor
from channel_database import ChannelDatabase
```

### Output Files
```
output/
├── VIDEO_ID_1.json    # Structured data
├── VIDEO_ID_1.txt     # Readable text
├── VIDEO_ID_2.json
└── VIDEO_ID_2.txt
```

## Size Reference

| Component | Files | Lines of Code | Documentation |
|-----------|-------|---------------|---------------|
| Source Code | 5 | ~600 | Type hints |
| Main App | 1 | ~500 | Inline comments |
| Documentation | 4 | ~2000 | Comprehensive |
| Examples | 1 | ~400 | Working code |
| **Total** | **11** | **~3500** | **Complete** |

## Getting Started Paths

### For End Users
1. Read: `README.md` (overview)
2. Read: `docs/QUICKSTART.md` (quick start)
3. Run: `./run.sh` (launch app)

### For Developers
1. Read: `README.md` (overview)
2. Read: `docs/ARCHITECTURE.md` (technical details)
3. Study: `src/` modules (source code)
4. Run: `docs/examples.py` (code examples)

### For Customization
1. Edit: `src/config.py` (API key, defaults)
2. Extend: `src/*.py` (add features)
3. Test: Run examples to verify

## Navigation Guide

```
Want to...                    → Go to...
─────────────────────────────────────────────────────
Understand the project        → README.md
Get started quickly           → docs/QUICKSTART.md
Learn the architecture        → docs/ARCHITECTURE.md
See code examples             → docs/examples.py
Configure settings            → src/config.py
Add YouTube API features      → src/youtube_api.py
Add transcript formats        → src/transcript_api.py
Modify BD channels data       → data/bangladeshi_channels.json
Understand this structure     → STRUCTURE.md (this file)
```

## File Sizes

```
app.py                          ~15 KB
src/youtube_api.py              ~7.5 KB
src/transcript_api.py           ~5.8 KB
src/channel_database.py         ~3.7 KB
src/config.py                   ~1.4 KB
data/bangladeshi_channels.json  ~45 KB
docs/ARCHITECTURE.md            ~25 KB
docs/examples.py                ~10 KB
README.md                       ~20 KB
```

## Quick Commands

```bash
# Navigate to project
cd youtube/youtube_transcript_collector

# Install dependencies
uv pip install -r requirements.txt

# Run app
./run.sh
# OR
uv run streamlit run app.py

# Run examples
uv run python docs/examples.py

# View structure
cat STRUCTURE.md

# Check all files
ls -R
```

## Summary

- **7 Python modules** (well organized)
- **1 Streamlit app** (clean UI)
- **4 documentation files** (comprehensive)
- **1 data file** (1000 BD channels)
- **Total**: Professional, production-ready structure

---

**Location**: `/Users/andy/Documents/projects/gen_ai/youtube/youtube_transcript_collector/`

**Ready to use!** Just run: `./run.sh`
