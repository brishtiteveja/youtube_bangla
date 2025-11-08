# 🚀 Quick Start Guide

## Installation (One-Time Setup)

### Step 1: Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Navigate to Project
```bash
cd youtube_transcript_collector
```

## Running the App

### Method 1: Quick Run (Easiest)
```bash
./run.sh
```

### Method 2: Manual
```bash
uv pip install -r requirements.txt
uv run streamlit run app.py
```

## First Time Usage (3 Steps)

### Step 1: Load Default Channel
1. Open app in browser (http://localhost:8501)
2. Click **"⭐ Load Default: Pinaki Bhattacharya"** in sidebar

### Step 2: Load Videos
1. Click **"📹 Load Videos"** button
2. Wait for videos to load (10-30 seconds)

### Step 3: Get Transcript
1. Expand any video
2. Click **"📝 Get Transcript"**
3. Download as JSON or TXT

**That's it! You've got your first transcript!**

## Common Tasks

### Task 1: Search BD Channels
```
1. Sidebar → "🇧🇩 Bangladeshi Channels" (default)
2. Filter box → Type "jamuna" or "prothom"
3. Select from dropdown
4. Click "Load"
```

### Task 2: Search Any Channel
```
1. Sidebar → "🔍 Search Any Channel"
2. Type channel name (e.g., "BBC News")
3. Click "Search"
4. Click on result to load
```

### Task 3: Load by URL
```
1. Sidebar → "🔗 Channel URL"
2. Paste: https://www.youtube.com/@ChannelName
3. Click "Load Channel"
```

### Task 4: Filter Videos
```
1. After loading videos
2. Use "🔍 Filter videos" box
3. Type keyword (e.g., "election", "বাজেট")
4. Only matching videos shown
```

### Task 5: Change Language
```
1. Before getting transcript
2. Select language: Bangla / English / Hindi / Auto
3. Then click "Get Transcript"
```

## Tips & Tricks

### 🎯 Faster Workflow
- Load 20 videos initially (faster)
- Use filters to find specific content
- Increase to 100+ for bulk work

### 📝 Best Transcript Format
- **Timestamped**: For reference, analysis
- **Plain text**: For reading, copying

### 💾 Download Strategy
- **JSON**: For data processing, archiving
- **TXT**: For reading, sharing

### 🔍 Power Search
Filter by keywords:
- "নির্বাচন" → Election videos
- "budget" → Budget videos
- "cricket" → Cricket videos
- "2024" → Recent videos

## Keyboard Shortcuts

In Streamlit app:
- `r` - Rerun app
- `c` - Clear cache
- `Ctrl+C` in terminal - Stop app

## Troubleshooting

### ❌ Error: "uv not found"
```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use regular pip
pip install -r requirements.txt
python -m streamlit run app.py
```

### ❌ Error: "No transcript found"
- Video doesn't have transcripts
- Try different language
- Use "Auto-detect"

### ❌ Error: "API quota exceeded"
- Wait 24 hours
- Or get your own API key (see README.md)

### ⏳ Slow Loading?
- Normal for 100+ videos
- Takes 30-60 seconds
- Has auto rate-limiting

## Next Steps

1. ✅ Try default channel (Pinaki)
2. ✅ Explore BD channels database
3. ✅ Search global channels
4. ✅ Download some transcripts
5. 📖 Read full README.md for advanced usage
6. 🔧 Check docs/ for code examples

---

Need help? Check **README.md** for full documentation!
