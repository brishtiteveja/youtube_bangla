# Tests Directory

This directory contains test scripts for the YouTube Transcript Collector.

## Test Files

### test_transcript.py

Tests the transcript fetching functionality.

**Usage:**
```bash
python tests/test_transcript.py
```

**Note:** If you encounter IP blocking errors from YouTube, wait a few minutes between test runs. YouTube rate-limits transcript requests to prevent abuse.

## Running Tests

From the project root:
```bash
# Run transcript tests
python tests/test_transcript.py
```

## Test Coverage

- ✅ TranscriptFetcher with multiple languages
- ✅ TranscriptProcessor formatting (timestamped and plain)
- ✅ Error handling for missing transcripts
- ✅ Language fallback mechanism

## Adding New Tests

1. Create a new test file in this directory
2. Import modules from `src/` using:
   ```python
   import sys
   import os
   sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
   ```
3. Document your test in this README
