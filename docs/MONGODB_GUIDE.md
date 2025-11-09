# MongoDB Management Guide

Complete guide for managing MongoDB cache in the YouTube Transcript Collector.

## Quick Start

### Check MongoDB Status
```bash
python src/mongodb_manager.py check
```

This shows:
- Connection status
- Collection existence and type
- Document counts
- Index information
- Time-series configuration

### Verify Setup
```bash
python src/mongodb_manager.py verify
```

Validates that everything is configured correctly.

### Run Tests
```bash
python tests/test_mongodb.py
```

Comprehensive tests that:
- Auto-fix setup issues
- Test all cache operations
- Verify data integrity
- Clean up test data

## Management Commands

### 1. Check Status
```bash
python src/mongodb_manager.py check
```

**Output Example:**
```
✅ Connected to: youtube_bangla

📦 CHANNELS
   Exists: ✅
   Time-series: ✅
   Documents: 15
   Indexes: 2
   Config: timeField=timestamp, metaField=metadata, granularity=hours
```

### 2. Fix Indexes
```bash
python src/mongodb_manager.py fix
```

Drops old indexes and recreates proper time-series indexes.

### 3. Recreate Collections
```bash
python src/mongodb_manager.py recreate
```

⚠️  **WARNING**: This deletes all cached data!

Drops and recreates collections as time-series collections.

### 4. Verify Setup
```bash
python src/mongodb_manager.py verify
```

Checks if setup is valid. Returns issues if found.

### 5. Clear Old Cache
```bash
# Clear cache older than 30 days (default)
python src/mongodb_manager.py clear

# Clear cache older than 7 days
python src/mongodb_manager.py clear 7
```

## MongoDB Structure

### Time-Series Collections

Three collections store cached data:

1. **channels** - Channel metadata
2. **videos** - Video lists from channels
3. **transcripts** - Video transcripts

### Document Structure

All documents follow this time-series structure:

```json
{
  "timestamp": "2025-11-08T12:00:00Z",  // Required timeField
  "metadata": {                          // Required metaField
    "channel_id": "UCxxx...",
    "channel_name": "Channel Name"
  },
  "data": {                              // Actual cached data
    "channel_id": "UCxxx...",
    "title": "Channel Name",
    "description": "...",
    ...
  }
}
```

### Indexes

Time-series collections use indexes on metadata fields:

- `channels`: `metadata.channel_id`, `metadata.channel_name`
- `videos`: `metadata.video_id`, `metadata.channel_id`
- `transcripts`: `metadata.video_id`

## Cache Expiration

Different data types have different TTLs:

- **Channels**: 7 days
- **Videos**: 1 day
- **Transcripts**: No expiration (permanent)

## Troubleshooting

### Issue: "Collection is not time-series"

**Cause**: Collections were created as regular collections before time-series was implemented.

**Fix**:
```bash
python src/mongodb_manager.py recreate
```

### Issue: "Duplicate key error"

**Cause**: Old indexes from regular collections conflicting with time-series structure.

**Fix**:
```bash
python src/mongodb_manager.py fix
```

### Issue: "MongoDB connection failed"

**Check**:
1. Is MongoDB running?
2. Is `MONGODB_URI` correct in `.env`?
3. Can you connect from command line?

```bash
mongosh "mongodb://admin:password@host:port/youtube_bangla?authSource=admin"
```

### Issue: "No data in MongoDB"

**This is normal** if:
- Collections were just recreated
- App hasn't cached any data yet

**Solution**: Run the app and load some channels. Data will be cached automatically.

## MongoDB with Docker (Optional)

If you want to run MongoDB locally:

```bash
# Start MongoDB
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:latest

# Update .env
MONGODB_URI=mongodb://admin:password@localhost:27017/youtube_bangla?authSource=admin
```

## Backup & Restore

### Backup
```bash
mongodump \
  --uri="mongodb://admin:password@host:port/youtube_bangla?authSource=admin" \
  --out=backup_$(date +%Y%m%d)
```

### Restore
```bash
mongorestore \
  --uri="mongodb://admin:password@host:port/youtube_bangla?authSource=admin" \
  backup_20250108/
```

## Monitoring

### View Cache Statistics
```python
from mongodb_cache import MongoDBCache

cache = MongoDBCache()
stats = cache.get_stats()
print(stats)
```

### Sample Output
```python
{
    'enabled': True,
    'channels_count': 15,
    'videos_count': 250,
    'transcripts_count': 120,
    'database': 'youtube_bangla'
}
```

## Best Practices

1. **Run tests after setup changes**
   ```bash
   python tests/test_mongodb.py
   ```

2. **Check status regularly**
   ```bash
   python src/mongodb_manager.py check
   ```

3. **Clear old cache periodically**
   ```bash
   python src/mongodb_manager.py clear 30
   ```

4. **Backup before recreating collections**
   ```bash
   mongodump --uri="..." --out=backup_$(date +%Y%m%d)
   python src/mongodb_manager.py recreate
   ```

## Configuration

### `.env` Settings

```bash
# Enable MongoDB caching
USE_MONGODB_CACHE=true

# MongoDB connection string
MONGODB_URI=mongodb://admin:password@host:port/youtube_bangla?authSource=admin

# Database name
MONGODB_DATABASE=youtube_bangla
```

## Advanced Usage

### Programmatic Access

```python
from mongodb_manager import MongoDBManager

# Create manager
manager = MongoDBManager()

# Check status
status = manager.check_status()

# Verify setup
is_valid, issues = manager.verify_setup()

if not is_valid:
    print("Issues found:")
    for issue in issues:
        print(f"  - {issue}")

# Fix if needed
if issues:
    manager.recreate_collections(confirm=True)

manager.close()
```

## Support

If you encounter issues not covered here:

1. Run diagnostic: `python tests/test_mongodb.py`
2. Check logs in the app output
3. Verify `.env` configuration
4. Test MongoDB connection directly

## Related Files

- `src/mongodb_cache.py` - Cache implementation
- `src/mongodb_manager.py` - Management utilities
- `tests/test_mongodb.py` - Comprehensive tests
- `.env` - Configuration