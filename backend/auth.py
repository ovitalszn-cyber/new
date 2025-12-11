"""
KashRock API - Authentication and API Key Management
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class APIKeyStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"

@dataclass
class APIKey:
    key: str
    name: str
    status: APIKeyStatus
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    rate_limit: int = 1000  # requests per hour
    notes: str = ""

class APIKeyManager:
    """Simple in-memory API key management for testing"""
    
    def __init__(self):
        self.keys: Dict[str, APIKey] = {}
        self.load_from_env()
    
    def load_from_env(self):
        """Load API keys from environment variables"""
        # Add a default test key for development
        test_key = APIKey(
            key="kr_test_key",
            name="test",
            status=APIKeyStatus.ACTIVE,
            created_at=datetime.utcnow(),
            rate_limit=1000
        )
        self.keys[test_key.key] = test_key
        
        # Load from environment variables like API_KEY_1, API_KEY_2, etc.
        for i in range(1, 11):  # Support up to 10 keys
            key_name = f"API_KEY_{i}"
            key_value = os.getenv(key_name)
            if key_value:
                # Parse key format: "name:key:status:rate_limit"
                parts = key_value.split(":")
                if len(parts) >= 2:
                    name = parts[0]
                    key = parts[1]
                    status = APIKeyStatus(parts[2]) if len(parts) > 2 else APIKeyStatus.ACTIVE
                    rate_limit = int(parts[3]) if len(parts) > 3 else 1000
                    
                    self.keys[key] = APIKey(
                        key=key,
                        name=name,
                        status=status,
                        created_at=datetime.now(),
                        rate_limit=rate_limit
                    )
    
    def generate_key(self, name: str, rate_limit: int = 1000, expires_days: Optional[int] = None) -> str:
        """Generate a new API key"""
        # Generate a secure random key
        key = f"kr_{secrets.token_urlsafe(32)}"
        
        expires_at = None
        if expires_days:
            expires_at = datetime.now() + timedelta(days=expires_days)
        
        api_key = APIKey(
            key=key,
            name=name,
            status=APIKeyStatus.ACTIVE,
            created_at=datetime.now(),
            expires_at=expires_at,
            rate_limit=rate_limit
        )
        
        self.keys[key] = api_key
        return key
    
    def validate_key(self, key: str) -> bool:
        """Validate an API key"""
        if key not in self.keys:
            return False
        
        api_key = self.keys[key]
        
        # Check if key is active
        if api_key.status != APIKeyStatus.ACTIVE:
            return False
        
        # Check if key is expired
        if api_key.expires_at and datetime.now() > api_key.expires_at:
            api_key.status = APIKeyStatus.EXPIRED
            return False
        
        # Update usage
        api_key.last_used = datetime.now()
        api_key.usage_count += 1
        
        return True
    
    def get_key_info(self, key: str) -> Optional[APIKey]:
        """Get information about an API key"""
        return self.keys.get(key)
    
    def list_keys(self) -> List[APIKey]:
        """List all API keys"""
        return list(self.keys.values())
    
    def deactivate_key(self, key: str) -> bool:
        """Deactivate an API key"""
        if key in self.keys:
            self.keys[key].status = APIKeyStatus.INACTIVE
            return True
        return False
    
    def activate_key(self, key: str) -> bool:
        """Activate an API key"""
        if key in self.keys:
            self.keys[key].status = APIKeyStatus.ACTIVE
            return True
        return False

# Global API key manager instance
api_key_manager = APIKeyManager()

def validate_api_key(authorization: str) -> bool:
    """Validate API key from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        return False
    
    key = authorization.replace("Bearer ", "").strip()
    
    # Ensure API keys are loaded (in case env vars were set after initialization)
    if not api_key_manager.keys:
        api_key_manager.load_from_env()
    
    return api_key_manager.validate_key(key)

def get_api_key_info(authorization: str) -> Optional[APIKey]:
    """Get API key information from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    key = authorization.replace("Bearer ", "").strip()
    return api_key_manager.get_key_info(key)

# Predefined test keys for immediate use
def create_test_keys():
    """Create some test API keys for immediate use"""
    test_keys = [
        ("tester_1", 1000, 30),  # name, rate_limit, expires_days
        ("tester_2", 1000, 30),
        ("tester_3", 500, 7),    # lower rate limit, shorter expiry
        ("admin", 10000, None),  # admin key, no expiry
    ]
    
    generated_keys = []
    for name, rate_limit, expires_days in test_keys:
        key = api_key_manager.generate_key(name, rate_limit, expires_days)
        generated_keys.append((name, key))
    
    return generated_keys

# Create test keys on import
if not api_key_manager.keys:
    create_test_keys()
