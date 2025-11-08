# 🏗️ Architecture Documentation

## Overview

YouTube Transcript Collector is a modular Python application built with clean architecture principles, separation of concerns, and type safety.

## Design Principles

1. **Modularity** - Each module has a single responsibility
2. **Separation of Concerns** - API, Business Logic, UI separated
3. **Type Safety** - Full type hints for better IDE support
4. **Caching** - Streamlit caching for performance
5. **Configuration Management** - Centralized config
6. **Error Handling** - Graceful error handling throughout

## Project Structure

```
youtube_transcript_collector/
│
├── src/                          # Source Code
│   ├── __init__.py              # Package exports
│   ├── config.py                # Configuration management
│   ├── youtube_api.py           # YouTube Data API client
│   ├── transcript_api.py        # Transcript operations
│   └── channel_database.py      # Database operations
│
├── data/                         # Data Files
│   └── bangladeshi_channels.json
│
├── output/                       # Generated Output
├── docs/                         # Documentation
│   ├── QUICKSTART.md
│   ├── ARCHITECTURE.md
│   └── examples.py
│
├── app.py                        # Streamlit Application
├── requirements.txt              # Dependencies
├── run.sh                        # Launch script
└── README.md                     # Main documentation
```

## Module Architecture

### Layer 1: Configuration (`config.py`)

**Purpose**: Centralized configuration management

**Class**: `Config`

**Responsibilities**:
- API keys
- Default values
- File paths
- Language settings
- UI configuration

**Usage**:
```python
from config import Config

api_key = Config.YOUTUBE_API_KEY
default_channel = Config.DEFAULT_CHANNEL
```

---

### Layer 2: Data Access

#### A. YouTube API Client (`youtube_api.py`)

**Purpose**: Handle all YouTube Data API v3 interactions

**Classes**:

1. **`YouTubeAPIClient`** (Low-level)
   - API request handling
   - Channel search
   - Channel info
   - Video listing

2. **`ChannelManager`** (High-level)
   - Channel operations
   - URL parsing
   - Auto-selection logic

**Methods**:
```python
# Low-level
api = YouTubeAPIClient(api_key)
channels = api.search_channels(query, max_results)
info = api.get_channel_info(channel_id)
videos = api.get_channel_videos(channel_id, max_results)

# High-level
manager = ChannelManager(api)
channel = manager.get_channel_by_url(url)
channel = manager.search_and_select(query)
```

**Design Decisions**:
- Separated low-level API calls from business logic
- Progress tracking optional (for CLI vs UI)
- Rate limiting built-in

#### B. Transcript API (`transcript_api.py`)

**Purpose**: Handle transcript fetching and formatting

**Classes**:

1. **`TranscriptFetcher`** (Data Access)
   - Fetch transcripts from YouTube
   - Language fallback logic
   - Error handling

2. **`TranscriptFormatter`** (Formatting)
   - Timestamped format
   - Plain text format
   - JSON format

3. **`TranscriptProcessor`** (High-level)
   - Combined fetch + format operations
   - Single API for common use cases

**Methods**:
```python
# Fetcher
fetcher = TranscriptFetcher()
result = fetcher.get_transcript(video_id, languages)

# Formatter
formatter = TranscriptFormatter()
text = formatter.format_timestamped(transcript)
text = formatter.format_plain_text(transcript)
data = formatter.to_json_dict(video_id, title, transcript)

# Processor (All-in-one)
processor = TranscriptProcessor()
result = processor.get_and_format(video_id, title, languages, format_type)
```

**Design Decisions**:
- Separated fetching from formatting
- Multiple output formats
- Metadata included in all operations

#### C. Channel Database (`channel_database.py`)

**Purpose**: Manage Bangladeshi channels database

**Class**: `ChannelDatabase`

**Methods**:
```python
db = ChannelDatabase()

# Query methods
all_channels = db.get_all_channels()
results = db.search_channels(query, limit)
channel = db.get_channel_by_rank(rank)
top = db.get_top_channels(count)

# Utility methods
names = db.get_channel_names()
formatted = db.format_for_display(channels)
stats = db.get_stats()
```

**Design Decisions**:
- Lazy loading from JSON
- Fast in-memory search
- UI-friendly formatting methods

---

### Layer 3: Presentation (`app.py`)

**Purpose**: Streamlit web interface

**Architecture**:
```
User Interface (Streamlit)
         ↓
Session State Management
         ↓
High-level APIs (Managers/Processors)
         ↓
Low-level APIs (Clients)
         ↓
External Services (YouTube)
```

**Key Features**:
- Component caching with `@st.cache_resource`
- Data caching with `@st.cache_data`
- Session state for user data
- Modular helper functions

---

## Data Flow

### Flow 1: Load Channel

```
User Input (Channel Name)
         ↓
ChannelManager.search_and_select()
         ↓
YouTubeAPIClient.search_channels()
         ↓
YouTube API
         ↓
ChannelManager.get_channel_info()
         ↓
Session State
         ↓
UI Update
```

### Flow 2: Get Transcript

```
User Input (Video ID)
         ↓
TranscriptProcessor.get_and_format()
         ↓
TranscriptFetcher.get_transcript()
         ↓
youtube-transcript-api
         ↓
TranscriptFormatter.format_*()
         ↓
Session State
         ↓
UI Display + Download
```

### Flow 3: Search BD Channels

```
User Input (Search Query)
         ↓
ChannelDatabase.search_channels()
         ↓
In-memory Search
         ↓
ChannelDatabase.format_for_display()
         ↓
UI Dropdown
         ↓
User Selection
         ↓
Flow 1 (Load Channel)
```

---

## Class Hierarchy

```
Config (Static Configuration)

YouTubeAPIClient (Low-level API)
    ↑
ChannelManager (High-level Operations)

TranscriptFetcher (Data Access)
    ↑
TranscriptFormatter (Formatting)
    ↑
TranscriptProcessor (Combined Operations)

ChannelDatabase (Data Management)

StreamlitApp (UI Layer)
    → Uses all above classes
```

---

## Caching Strategy

### Resource Caching
```python
@st.cache_resource
def get_api_client():
    return YouTubeAPIClient(Config.YOUTUBE_API_KEY)
```

**Used for**:
- API clients
- Managers
- Processors
- Database instances

**Why**: These objects are stateless and expensive to create

### Data Caching
```python
@st.cache_data
def get_channel_database():
    return ChannelDatabase()
```

**Used for**:
- Database loading
- Static data

**Why**: Data doesn't change between runs

---

## Error Handling

### API Errors
```python
try:
    result = api.search_channels(query)
except Exception as e:
    return {'error': str(e)}
```

### Transcript Errors
```python
try:
    transcript = fetch_transcript(video_id)
except NoTranscriptFound:
    return {'success': False, 'error': 'No transcript found'}
except TranscriptsDisabled:
    return {'success': False, 'error': 'Transcripts disabled'}
```

### UI Errors
```python
if not result['success']:
    st.error(f"❌ {result['error']}")
else:
    st.success("✅ Success!")
```

---

## Type System

### Type Hints

```python
def get_transcript(
    video_id: str,
    languages: List[str] = None
) -> Dict:
    """
    Get transcript for video

    Args:
        video_id: YouTube video ID
        languages: List of language codes

    Returns:
        Dictionary with success status and data
    """
```

### Return Types

**Success Response**:
```python
{
    'success': True,
    'transcript': [...],
    'language_code': 'bn',
    'is_generated': True
}
```

**Error Response**:
```python
{
    'success': False,
    'error': 'Error message'
}
```

---

## Configuration Management

### Centralized Config
```python
class Config:
    # API
    YOUTUBE_API_KEY = 'key'

    # Defaults
    DEFAULT_CHANNEL = 'Pinaki Bhattacharya'
    DEFAULT_VIDEO_COUNT = 50

    # Paths
    PROJECT_ROOT = ...
    DATA_DIR = ...
    OUTPUT_DIR = ...
```

### Benefits:
1. Single source of truth
2. Easy to modify
3. Type-safe access
4. Environment-specific configs possible

---

## Testing Strategy

### Unit Testing (Recommended)
```python
# Test fetcher
fetcher = TranscriptFetcher()
result = fetcher.get_transcript("VIDEO_ID")
assert result['success'] == True

# Test formatter
formatter = TranscriptFormatter()
text = formatter.format_timestamped(transcript)
assert '[00:00]' in text

# Test database
db = ChannelDatabase()
results = db.search_channels("test")
assert len(results) > 0
```

### Integration Testing
```python
# Test full flow
processor = TranscriptProcessor()
result = processor.get_and_format(
    video_id="VIDEO_ID",
    video_title="Title",
    languages=['bn']
)
assert result['success'] == True
assert 'formatted_text' in result
```

---

## Performance Optimization

### 1. Caching
- Streamlit resource caching for clients
- Data caching for database
- Session state for user data

### 2. Rate Limiting
- Built-in delays (0.3s) between API calls
- Prevents quota exhaustion

### 3. Lazy Loading
- Database loaded on first use
- Videos loaded on demand

### 4. Pagination
- Videos fetched in batches of 50
- User-controlled limits

---

## Security Considerations

### 1. API Key Management
- Stored in config file (not in code)
- Should use environment variables in production

### 2. Input Validation
- All user inputs validated
- URL parsing with error handling

### 3. Rate Limiting
- Built-in to prevent abuse
- Respects YouTube API limits

---

## Extension Points

### Add New Transcript Format
```python
# In TranscriptFormatter class
@staticmethod
def format_custom(transcript: List[Dict]) -> str:
    # Custom formatting logic
    pass
```

### Add New API Endpoint
```python
# In YouTubeAPIClient class
def get_playlist_videos(self, playlist_id: str) -> List[Dict]:
    # Implementation
    pass
```

### Add New Database Source
```python
# New class similar to ChannelDatabase
class GlobalChannelDatabase:
    def __init__(self, source: str):
        # Load from different source
        pass
```

---

## Dependencies

### Core
- `streamlit` - Web framework
- `requests` - HTTP client
- `youtube-transcript-api` - Transcript fetching

### Optional
- `pandas` - Data manipulation (listed but not used yet)

### Development
- `uv` - Package manager (recommended)
- Python 3.8+

---

## Future Enhancements

### Potential Features
1. Batch export to CSV/Excel
2. Transcript search across videos
3. Analytics dashboard
4. Scheduled scraping
5. Multi-user support
6. Database backend (SQLite/PostgreSQL)

### Architecture Changes
1. Add service layer between UI and data access
2. Implement repository pattern
3. Add unit tests
4. Add logging framework
5. Add async support for parallel fetching

---

**Version**: 1.0.0
**Last Updated**: 2024
