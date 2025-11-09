#!/usr/bin/env python3
"""
MongoDB Manager
Comprehensive MongoDB management tool for checking, fixing, and recreating collections
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import Config


class MongoDBManager:
    """Manage MongoDB collections, indexes, and data"""

    def __init__(self):
        """Initialize MongoDB manager"""
        self.client = None
        self.db = None
        self.connected = False
        self._connect()

    def _connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.client.server_info()
            self.db = self.client[Config.MONGODB_DATABASE]
            self.connected = True
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            self.connected = False
            return False

    def check_status(self) -> Dict:
        """
        Check MongoDB status and return detailed information

        Returns:
            Dictionary with status information
        """
        if not self.connected:
            return {
                'connected': False,
                'error': 'Not connected to MongoDB'
            }

        try:
            collections = self.db.list_collection_names()

            status = {
                'connected': True,
                'database': Config.MONGODB_DATABASE,
                'collections': {},
                'issues': []
            }

            # Check each collection
            for coll_name in ['channels', 'videos', 'transcripts']:
                coll_status = {
                    'exists': coll_name in collections,
                    'is_timeseries': False,
                    'document_count': 0,
                    'indexes': []
                }

                if coll_name in collections:
                    # Check if time-series
                    coll_info = self.db.command('listCollections', filter={'name': coll_name})
                    if coll_info['cursor']['firstBatch']:
                        info = coll_info['cursor']['firstBatch'][0]
                        options = info.get('options', {})

                        if 'timeseries' in options:
                            coll_status['is_timeseries'] = True
                            coll_status['timeseries_config'] = options['timeseries']
                        else:
                            status['issues'].append(f"{coll_name} is not a time-series collection")

                    # Get document count
                    coll_status['document_count'] = self.db[coll_name].count_documents({})

                    # Get indexes
                    indexes = list(self.db[coll_name].list_indexes())
                    coll_status['indexes'] = [idx['name'] for idx in indexes]

                else:
                    status['issues'].append(f"{coll_name} collection does not exist")

                status['collections'][coll_name] = coll_status

            return status

        except Exception as e:
            return {
                'connected': True,
                'error': str(e)
            }

    def print_status(self):
        """Print formatted status information"""
        status = self.check_status()

        print("=" * 70)
        print("MongoDB Status Check")
        print("=" * 70)
        print()

        if not status.get('connected'):
            print(f"❌ {status.get('error', 'Connection failed')}")
            return

        print(f"✅ Connected to: {status['database']}")
        print()

        # Print collection status
        for coll_name, coll_info in status['collections'].items():
            print(f"📦 {coll_name.upper()}")
            print(f"   Exists: {'✅' if coll_info['exists'] else '❌'}")

            if coll_info['exists']:
                print(f"   Time-series: {'✅' if coll_info['is_timeseries'] else '❌'}")
                print(f"   Documents: {coll_info['document_count']}")
                print(f"   Indexes: {len(coll_info['indexes'])}")

                if coll_info.get('timeseries_config'):
                    ts_config = coll_info['timeseries_config']
                    print(f"   Config: timeField={ts_config.get('timeField')}, "
                          f"metaField={ts_config.get('metaField')}, "
                          f"granularity={ts_config.get('granularity')}")
            print()

        # Print issues
        if status.get('issues'):
            print("⚠️  ISSUES FOUND:")
            for issue in status['issues']:
                print(f"   - {issue}")
            print()

        print("=" * 70)

    def fix_indexes(self) -> bool:
        """
        Fix indexes - drop old ones and recreate proper time-series indexes

        Returns:
            True if successful
        """
        if not self.connected:
            print("❌ Not connected to MongoDB")
            return False

        print("=" * 70)
        print("Fixing Indexes")
        print("=" * 70)
        print()

        try:
            collections = self.db.list_collection_names()

            for coll_name in ['channels', 'videos', 'transcripts']:
                if coll_name not in collections:
                    print(f"⚠️  {coll_name} collection doesn't exist (skipping)")
                    continue

                print(f"Fixing {coll_name} indexes...")
                collection = self.db[coll_name]

                # List and drop old indexes
                indexes = list(collection.list_indexes())
                for idx in indexes:
                    if idx['name'] != '_id_':
                        try:
                            collection.drop_index(idx['name'])
                            print(f"   ✅ Dropped {idx['name']}")
                        except Exception as e:
                            print(f"   ⚠️  Could not drop {idx['name']}: {str(e)}")

            print()
            print("Creating time-series indexes...")

            # Recreate proper indexes
            index_specs = [
                ('channels', [("metadata.channel_id", 1)]),
                ('channels', [("metadata.channel_name", 1)]),
                ('videos', [("metadata.video_id", 1)]),
                ('videos', [("metadata.channel_id", 1)]),
                ('transcripts', [("metadata.video_id", 1)])
            ]

            for coll_name, index_spec in index_specs:
                if coll_name in collections:
                    try:
                        self.db[coll_name].create_index(index_spec)
                        field_name = index_spec[0][0]
                        print(f"   ✅ Created index: {coll_name}.{field_name}")
                    except Exception as e:
                        print(f"   ⚠️  {coll_name}.{field_name}: {str(e)}")

            print()
            print("=" * 70)
            print("✅ Index fix completed!")
            print("=" * 70)
            return True

        except Exception as e:
            print(f"❌ Error fixing indexes: {str(e)}")
            return False

    def recreate_collections(self, confirm: bool = False) -> bool:
        """
        Drop and recreate collections as time-series

        Args:
            confirm: Skip confirmation prompt if True

        Returns:
            True if successful
        """
        if not self.connected:
            print("❌ Not connected to MongoDB")
            return False

        print("=" * 70)
        print("Recreate Time-Series Collections")
        print("=" * 70)
        print()
        print("⚠️  WARNING: This will delete all existing cached data!")
        print("   The app will re-fetch and cache data as needed.")
        print()

        if not confirm:
            response = input("Continue? (yes/no): ").strip().lower()
            if response != 'yes':
                print("Cancelled.")
                return False
            print()

        try:
            collections = ['channels', 'videos', 'transcripts']

            # Drop old collections
            print("1. Dropping old collections...")
            for coll_name in collections:
                if coll_name in self.db.list_collection_names():
                    self.db[coll_name].drop()
                    print(f"   ✅ Dropped {coll_name}")
                else:
                    print(f"   ℹ️  {coll_name} doesn't exist (skipping)")
            print()

            # Create time-series collections
            print("2. Creating time-series collections...")
            timeseries_config = {
                'timeField': 'timestamp',
                'metaField': 'metadata',
                'granularity': 'hours'
            }

            for coll_name in collections:
                try:
                    self.db.create_collection(coll_name, timeseries=timeseries_config)
                    print(f"   ✅ Created time-series collection: {coll_name}")
                except Exception as e:
                    print(f"   ❌ Error creating {coll_name}: {str(e)}")
            print()

            # Create indexes
            print("3. Creating indexes...")
            self.fix_indexes()

            print()
            print("=" * 70)
            print("✅ Collections recreated successfully!")
            print("=" * 70)
            return True

        except Exception as e:
            print(f"❌ Error recreating collections: {str(e)}")
            return False

    def verify_setup(self) -> Tuple[bool, List[str]]:
        """
        Verify MongoDB setup is correct

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        status = self.check_status()

        if not status.get('connected'):
            return False, [status.get('error', 'Not connected')]

        issues = status.get('issues', [])

        # Additional checks
        # Expected index counts: channels=2, videos=2, transcripts=1
        expected_indexes = {
            'channels': 2,
            'videos': 2,
            'transcripts': 1
        }

        for coll_name, coll_info in status['collections'].items():
            if not coll_info['exists']:
                issues.append(f"{coll_name} collection missing")
            elif not coll_info['is_timeseries']:
                issues.append(f"{coll_name} is not time-series")
            elif len(coll_info['indexes']) < expected_indexes.get(coll_name, 1):
                expected = expected_indexes.get(coll_name, 1)
                actual = len(coll_info['indexes'])
                issues.append(f"{coll_name} has insufficient indexes (expected {expected}, got {actual})")

        return len(issues) == 0, issues

    def get_sample_data(self, collection: str, limit: int = 5) -> List[Dict]:
        """
        Get sample documents from a collection

        Args:
            collection: Collection name
            limit: Number of documents to retrieve

        Returns:
            List of documents
        """
        if not self.connected:
            return []

        try:
            return list(self.db[collection].find().limit(limit))
        except Exception as e:
            print(f"Error getting sample data: {str(e)}")
            return []

    def clear_old_cache(self, days: int = 30):
        """
        Clear cache older than specified days

        Args:
            days: Age threshold in days
        """
        if not self.connected:
            print("❌ Not connected to MongoDB")
            return

        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            print(f"Clearing cache older than {days} days...")

            channels_deleted = self.db.channels.delete_many({'timestamp': {'$lt': cutoff}})
            videos_deleted = self.db.videos.delete_many({'timestamp': {'$lt': cutoff}})
            transcripts_deleted = self.db.transcripts.delete_many({'timestamp': {'$lt': cutoff}})

            print(f"✅ Cleared: {channels_deleted.deleted_count} channels, "
                  f"{videos_deleted.deleted_count} videos, "
                  f"{transcripts_deleted.deleted_count} transcripts")

        except Exception as e:
            print(f"Error clearing cache: {str(e)}")

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False


def main():
    """Main CLI interface"""
    import sys

    if len(sys.argv) < 2:
        print("MongoDB Manager")
        print()
        print("Usage:")
        print("  python mongodb_manager.py check        - Check MongoDB status")
        print("  python mongodb_manager.py fix          - Fix indexes")
        print("  python mongodb_manager.py recreate     - Recreate collections")
        print("  python mongodb_manager.py verify       - Verify setup")
        print("  python mongodb_manager.py clear [days] - Clear old cache (default: 30 days)")
        return

    command = sys.argv[1].lower()
    manager = MongoDBManager()

    try:
        if command == 'check':
            manager.print_status()

        elif command == 'fix':
            manager.fix_indexes()

        elif command == 'recreate':
            manager.recreate_collections()

        elif command == 'verify':
            is_valid, issues = manager.verify_setup()
            if is_valid:
                print("✅ MongoDB setup is correct!")
            else:
                print("❌ MongoDB setup has issues:")
                for issue in issues:
                    print(f"   - {issue}")
                print()
                print("Run 'python mongodb_manager.py recreate' to fix.")

        elif command == 'clear':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            manager.clear_old_cache(days)

        else:
            print(f"Unknown command: {command}")

    finally:
        manager.close()


if __name__ == '__main__':
    main()