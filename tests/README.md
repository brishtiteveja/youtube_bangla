# Tests

MongoDB cache tests for the YouTube Transcript Collector.

## Running Tests

```bash
# Run all MongoDB tests
python tests/test_mongodb.py

# Or from project root
cd tests && python test_mongodb.py
```

## What Gets Tested

1. **Channel Caching**
   - Write channel data to MongoDB
   - Read channel data from cache
   - Verify data integrity

2. **Videos Caching**
   - Write multiple videos to MongoDB
   - Read videos from cache
   - Verify correct number of videos

3. **Transcript Caching**
   - Write transcript data to MongoDB
   - Read transcript from cache
   - Verify transcript structure

4. **Cache Statistics**
   - Get cache statistics
   - Verify counts are accurate

5. **Time-Series Structure**
   - Verify documents have timestamp field
   - Verify documents have metadata field
   - Verify documents have data field

## Auto-Fix

The test will automatically check if MongoDB is set up correctly:
- If collections don't exist → Creates them
- If collections aren't time-series → Recreates them
- If indexes are missing → Creates them

## Test Data

Test data is automatically cleaned up after tests complete.

Test data uses these identifiers:
- Channel ID: TEST_CHANNEL_123
- Video IDs: TEST_VIDEO_1, TEST_VIDEO_2
