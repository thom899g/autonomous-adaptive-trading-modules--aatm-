"""
Firebase State Manager for AATM
Handles persistence of strategies, performance data, and market state
"""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.collection import CollectionReference
import hashlib
from aatm_config import config, logger

class StateManager:
    """Manages persistent state using Firebase Firestore"""
    
    def __init__(self):
        """Initialize Firebase connection"""
        self.client: Optional[FirestoreClient] = None
        self._initialized = False
        self._initialize_firebase()
        
    def _initialize_firebase(self) -> None:
        """Initialize Firebase Admin SDK with error handling"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                if not config.firebase.credentials_path:
                    raise ValueError("Firebase credentials path not configured")
                
                cred = credentials.Certificate(config.firebase.credentials_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': config.firebase.project_id
                })
                logger.info(f"Firebase initialized for project: {config.firebase.project_id}")
            
            self.client = firestore.client()
            self._initialized = True
            
            # Test connection
            self._test_connection()
            
        except FileNotFoundError as e:
            logger.error(f"Firebase credentials file not found: {e}")
            raise
        except ValueError as e:
            logger.error(f"Firebase initialization error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected Firebase error: {e}")
            raise
    
    def _test_connection(self) -> None:
        """Test Firebase connection with timeout"""
        import concurrent.futures
        
        def connection_test():
            try:
                # Simple read operation to test connection
                doc_ref = self.client.collection('test').document('connection_test')
                doc_ref.set({'timestamp': datetime.now(timezone.utc)}, merge=True)
                doc_ref.delete()
                return True
            except Exception as e:
                logger.error(f"Firebase connection test failed: {e}")
                return False
        
        # Run with timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(connection_test)
            try:
                success = future.result(timeout=