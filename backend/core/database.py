from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def get_database():
    return db_instance.db

async def init_db():
    try:
        db_instance.client = AsyncIOMotorClient(settings.MONGO_URL)
        db_instance.db = db_instance.client[settings.DB_NAME]
        
        # Test connection
        await db_instance.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.DB_NAME}")
        
        # Create indexes
        await create_indexes()
        
        # Initialize superadmin
        from services.auth_service import AuthService
        await AuthService.create_superadmin()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def create_indexes():
    """Create database indexes for performance"""
    db = db_instance.db
    
    # Users indexes
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email")
    
    # NFA indexes
    await db.nfa_requests.create_index("nfa_number", unique=True, sparse=True)
    await db.nfa_requests.create_index("requestor_id")
    await db.nfa_requests.create_index("status")
    await db.nfa_requests.create_index("created_at")
    
    # Approval workflows indexes
    await db.approval_workflows.create_index([("nfa_id", 1), ("section", 1), ("sequence", 1)])
    await db.approval_workflows.create_index("approver_id")
    await db.approval_workflows.create_index("status")
    
    # Vendors indexes
    await db.vendors.create_index("name")
    await db.vendors.create_index("status")
    
    logger.info("Database indexes created")

async def close_db():
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed")
