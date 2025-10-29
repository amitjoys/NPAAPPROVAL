from fastapi import APIRouter, Depends
from core.security import require_role
from core.database import get_database
from models.schemas import UserRole
from typing import Dict

router = APIRouter()

@router.get("/stats")
async def get_admin_stats(
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN]))
):
    """Get comprehensive admin statistics"""
    db = await get_database()
    
    # Get counts
    total_users = await db.users.count_documents({})
    total_nfas = await db.nfa_requests.count_documents({})
    total_vendors = await db.vendors.count_documents({})
    total_approvals = await db.approval_workflows.count_documents({})
    
    # Get pending counts
    pending_approvals = await db.approval_workflows.count_documents({"status": "pending"})
    pending_nfas = await db.nfa_requests.count_documents({
        "status": {"$in": ["section1_pending", "section2_pending"]}
    })
    
    # Get recent activity
    recent_nfas = await db.nfa_requests.find(
        {},
        {"_id": 0, "id": 1, "nfa_number": 1, "status": 1, "requestor_name": 1, "created_at": 1}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    return {
        "totals": {
            "users": total_users,
            "nfas": total_nfas,
            "vendors": total_vendors,
            "approvals": total_approvals
        },
        "pending": {
            "approvals": pending_approvals,
            "nfas": pending_nfas
        },
        "recent_nfas": recent_nfas
    }

@router.post("/clear-database")
async def clear_database(
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN]))
):
    """Clear all data except users (SuperAdmin only - use with caution)"""
    db = await get_database()
    
    # Delete NFAs
    nfa_result = await db.nfa_requests.delete_many({})
    
    # Delete approvals
    approval_result = await db.approval_workflows.delete_many({})
    
    # Delete attachments
    attachment_result = await db.attachments.delete_many({})
    
    return {
        "message": "Database cleared",
        "deleted": {
            "nfas": nfa_result.deleted_count,
            "approvals": approval_result.deleted_count,
            "attachments": attachment_result.deleted_count
        }
    }

@router.get("/system-health")
async def get_system_health(
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN]))
):
    """Get system health status"""
    db = await get_database()
    
    # Test database connection
    try:
        await db.command('ping')
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Test Redis connection
    try:
        from tasks.celery_app import celery_app
        celery_status = celery_app.control.ping(timeout=1.0)
        redis_status = "healthy" if celery_status else "unhealthy"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    return {
        "database": db_status,
        "redis": redis_status,
        "overall": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded"
    }
