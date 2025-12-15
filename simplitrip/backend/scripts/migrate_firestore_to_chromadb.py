"""
Migration script: Firestore → ChromaDB
Migrates existing user trips from Firebase Firestore to ChromaDB

Usage:
    python migrate_firestore_to_chromadb.py --user-id user123
    python migrate_firestore_to_chromadb.py --all-users
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import logger

try:
    from firebase_admin import db as firebase_db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase not available - migration mode limited")

from services.trip_storage_service import TripStorageService

class FirestoreToChromaDBMigration:
    """Handles migration of trips from Firestore to ChromaDB"""
    
    def __init__(self):
        self.trip_storage = TripStorageService()
        self.migrated_count = 0
        self.failed_count = 0
        self.error_messages = []
    
    def migrate_user_trips(self, user_id: str) -> bool:
        """
        Migrate all trips for a specific user from Firestore to ChromaDB
        
        Args:
            user_id: Firebase user ID
            
        Returns:
            True if migration successful, False otherwise
        """
        logger.info(f"🔄 Starting migration for user: {user_id}")
        
        try:
            if not FIREBASE_AVAILABLE:
                logger.warning("Firebase SDK not available - cannot fetch from Firestore")
                return False
            
            # Fetch trips from Firestore
            # Note: This assumes standard Firestore collection structure
            firestore_trips = self._fetch_firestore_trips(user_id)
            
            if not firestore_trips:
                logger.warning(f"No trips found in Firestore for user: {user_id}")
                return False
            
            logger.info(f"Found {len(firestore_trips)} trips in Firestore")
            
            # Migrate each trip
            for trip_id, trip_data in firestore_trips.items():
                try:
                    self._migrate_single_trip(user_id, trip_id, trip_data)
                    self.migrated_count += 1
                except Exception as e:
                    logger.error(f"Failed to migrate trip {trip_id}: {e}")
                    self.failed_count += 1
                    self.error_messages.append(f"Trip {trip_id}: {str(e)}")
            
            logger.info(f"✅ Migration complete for user {user_id}")
            logger.info(f"   Migrated: {self.migrated_count}, Failed: {self.failed_count}")
            
            return self.failed_count == 0
            
        except Exception as e:
            logger.error(f"❌ Migration error for user {user_id}: {e}")
            return False
    
    def _fetch_firestore_trips(self, user_id: str) -> dict:
        """
        Fetch trips from Firestore
        
        Assumes structure: /users/{user_id}/trips/{trip_id}
        """
        try:
            # This is a template - adjust path based on actual Firestore structure
            ref = firebase_db.reference(f"users/{user_id}/trips")
            trips = ref.get()
            return trips.val() if trips else {}
        except Exception as e:
            logger.error(f"Error fetching from Firestore: {e}")
            return {}
    
    def _migrate_single_trip(self, user_id: str, trip_id: str, trip_data: dict):
        """
        Migrate a single trip to ChromaDB
        
        Args:
            user_id: Firebase user ID
            trip_id: Trip ID from Firestore
            trip_data: Trip data dictionary
        """
        # Ensure required fields
        if not isinstance(trip_data, dict):
            raise ValueError(f"Invalid trip data format for {trip_id}")
        
        # Build trip object for ChromaDB
        trip_object = {
            "trip_id": trip_id,
            "user_id": user_id,
            "destination": trip_data.get("destination", "Unknown"),
            "start_date": trip_data.get("start_date"),
            "end_date": trip_data.get("end_date"),
            "budget": trip_data.get("budget"),
            "preferences": trip_data.get("preferences", []),
            "flights": trip_data.get("flights", []),
            "itinerary": trip_data.get("itinerary", []),
            "accommodation": trip_data.get("accommodation", {}),
            "created_at": trip_data.get("created_at", datetime.now().isoformat()),
            "updated_at": trip_data.get("updated_at", datetime.now().isoformat()),
            # Preserve any additional fields
            **{k: v for k, v in trip_data.items() 
               if k not in ["trip_id", "user_id", "destination", "start_date", "end_date", 
                           "budget", "preferences", "flights", "itinerary", "accommodation",
                           "created_at", "updated_at"]}
        }
        
        # Add to ChromaDB
        self.trip_storage.add_trip(user_id, trip_object)
        logger.info(f"   ✅ Migrated trip: {trip_id} to {trip_object.get('destination', 'N/A')}")
    
    def migrate_all_users(self) -> dict:
        """
        Migrate trips for all users from Firestore to ChromaDB
        
        Returns:
            Dictionary with migration statistics
        """
        logger.info("🔄 Starting migration for ALL users")
        
        try:
            if not FIREBASE_AVAILABLE:
                logger.error("Firebase SDK not available")
                return {"error": "Firebase not available"}
            
            # Fetch all users
            users_ref = firebase_db.reference("users")
            users_data = users_ref.get()
            
            if not users_data or not users_data.val():
                logger.warning("No users found in Firestore")
                return {"users_processed": 0, "trips_migrated": 0}
            
            user_ids = list(users_data.val().keys())
            logger.info(f"Found {len(user_ids)} users to process")
            
            # Process each user
            users_processed = 0
            users_failed = 0
            
            for user_id in user_ids:
                try:
                    if self.migrate_user_trips(user_id):
                        users_processed += 1
                    else:
                        users_failed += 1
                except Exception as e:
                    logger.error(f"Error processing user {user_id}: {e}")
                    users_failed += 1
            
            logger.info(f"\n" + "=" * 60)
            logger.info(f"Migration Summary:")
            logger.info(f"  Users processed: {users_processed}")
            logger.info(f"  Users failed: {users_failed}")
            logger.info(f"  Total trips migrated: {self.migrated_count}")
            logger.info(f"  Total trips failed: {self.failed_count}")
            logger.info("=" * 60)
            
            return {
                "users_processed": users_processed,
                "users_failed": users_failed,
                "trips_migrated": self.migrated_count,
                "trips_failed": self.failed_count,
                "errors": self.error_messages
            }
            
        except Exception as e:
            logger.error(f"❌ Error in migrate_all_users: {e}")
            return {"error": str(e)}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Migrate trips from Firestore to ChromaDB"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        help="Migrate trips for a specific user ID"
    )
    parser.add_argument(
        "--all-users",
        action="store_true",
        help="Migrate trips for all users"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without actually migrating"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Firestore → ChromaDB Migration Tool")
    logger.info("=" * 60)
    
    if not FIREBASE_AVAILABLE:
        logger.error("❌ Firebase Admin SDK not available")
        logger.info("Install with: pip install firebase-admin")
        sys.exit(1)
    
    migrator = FirestoreToChromaDBMigration()
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made")
    
    if args.user_id:
        result = migrator.migrate_user_trips(args.user_id)
        sys.exit(0 if result else 1)
    
    elif args.all_users:
        result = migrator.migrate_all_users()
        logger.info(f"Migration result: {result}")
        sys.exit(0)
    
    else:
        parser.print_help()
        logger.warning("Please specify --user-id or --all-users")
        sys.exit(1)


if __name__ == "__main__":
    main()
