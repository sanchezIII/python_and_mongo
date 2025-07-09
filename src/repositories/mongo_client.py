"""MongoDB client for database operations."""

import logging
from typing import Optional, Dict, Any
from pymongo import MongoClient as PyMongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
from bson.errors import InvalidId


class MongoClient:
    """MongoDB client wrapper for database operations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize MongoDB client."""
        self.config = config
        self.client: Optional[PyMongoClient] = None
        self.database: Optional[Database] = None
        self.logger = logging.getLogger(__name__)
        
        self._connect()
    
    def _connect(self) -> None:
        """Connect to MongoDB."""
        try:
            mongodb_uri = self.config.get('MONGODB_URI')
            if not mongodb_uri:
                raise ValueError("MONGODB_URI not configured")
            
            self.client = PyMongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database
            database_name = self.config.get('MONGODB_DATABASE', 'flask_db')
            self.database = self.client[database_name]
            
            self.logger.info(f"Connected to MongoDB database: {database_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
            raise
    
    def get_database(self) -> Database:
        """Get database instance."""
        if self.database is None:
            raise RuntimeError("Database not initialized")
        return self.database
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get collection instance."""
        return self.get_database()[collection_name]
    
    def close(self) -> None:
        """Close database connection."""
        if self.client is not None:
            self.client.close()
            self.logger.info("MongoDB connection closed")
    
    def ping(self) -> bool:
        """Check if database is available."""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            self.logger.error(f"Database ping failed: {str(e)}")
            return False
    
    @staticmethod
    def is_valid_object_id(oid: str) -> bool:
        """Check if string is a valid ObjectId."""
        try:
            ObjectId(oid)
            return True
        except (InvalidId, TypeError):
            return False
    
    @staticmethod
    def to_object_id(oid: str) -> ObjectId:
        """Convert string to ObjectId."""
        if not MongoClient.is_valid_object_id(oid):
            raise ValueError(f"Invalid ObjectId: {oid}")
        return ObjectId(oid)
    
    def create_indexes(self) -> None:
        """Create database indexes."""
        try:
            # Customer indexes
            customers = self.get_collection('customers')
            customers.create_index('email', unique=True)
            customers.create_index('created_at')
            
            # Subscription indexes
            subscriptions = self.get_collection('subscriptions')
            subscriptions.create_index('customer_id')
            subscriptions.create_index('product_id')
            subscriptions.create_index('status')
            subscriptions.create_index('created_at')
            
            self.logger.info("Database indexes created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create indexes: {str(e)}")
            raise
    
    def drop_database(self) -> None:
        """Drop the entire database (use with caution)."""
        if self.database is not None:
            database_name = self.database.name
            self.client.drop_database(database_name)
            self.logger.warning(f"Database '{database_name}' dropped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            stats = self.database.command('dbstats')
            return {
                'database': stats.get('db'),
                'collections': stats.get('collections'),
                'documents': stats.get('objects'),
                'data_size': stats.get('dataSize'),
                'storage_size': stats.get('storageSize'),
                'indexes': stats.get('indexes')
            }
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {str(e)}")
            return {} 