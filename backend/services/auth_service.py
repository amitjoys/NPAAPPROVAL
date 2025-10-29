from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from core.database import get_database
from core.security import SecurityService
from core.config import settings
from models.schemas import UserCreate, UserRole, UserResponse
import logging
import uuid

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> Dict[str, Any]:
        """Create a new user"""
        db = await get_database()
        
        # Check if username exists
        existing_user = await db.users.find_one({"username": user_data.username})
        if existing_user:
            raise ValueError("Username already exists")
        
        # Check if email exists
        existing_email = await db.users.find_one({"email": user_data.email})
        if existing_email:
            raise ValueError("Email already exists")
        
        # Hash password
        hashed_password = SecurityService.hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "id": str(uuid.uuid4()),
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": hashed_password,
            "name": user_data.name,
            "designation": user_data.designation,
            "department": user_data.department,
            "location": user_data.location,
            "function": user_data.function,
            "roles": [role.value for role in user_data.roles],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.users.insert_one(user_doc)
        logger.info(f"User created: {user_data.username}")
        
        # Remove password hash from response
        user_doc.pop("password_hash", None)
        user_doc.pop("_id", None)
        return user_doc
    
    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data"""
        db = await get_database()
        
        user = await db.users.find_one({"username": username})
        if not user:
            return None
        
        if not SecurityService.verify_password(password, user["password_hash"]):
            return None
        
        if not user.get("is_active", True):
            return None
        
        # Remove sensitive data
        user.pop("password_hash", None)
        user.pop("_id", None)
        return user
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        db = await get_database()
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
        return user
    
    @staticmethod
    async def create_superadmin():
        """Create superadmin user if not exists"""
        db = await get_database()
        
        existing = await db.users.find_one({"username": settings.SUPERADMIN_USERNAME})
        if existing:
            logger.info("SuperAdmin already exists")
            return
        
        hashed_password = SecurityService.hash_password(settings.SUPERADMIN_PASSWORD)
        
        superadmin_doc = {
            "id": str(uuid.uuid4()),
            "username": settings.SUPERADMIN_USERNAME,
            "email": settings.SUPERADMIN_EMAIL,
            "password_hash": hashed_password,
            "name": "Super Administrator",
            "designation": "System Administrator",
            "department": "IT",
            "location": "HQ",
            "function": "Administration",
            "roles": [UserRole.SUPERADMIN.value],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.users.insert_one(superadmin_doc)
        logger.info(f"SuperAdmin created: {settings.SUPERADMIN_USERNAME}")
