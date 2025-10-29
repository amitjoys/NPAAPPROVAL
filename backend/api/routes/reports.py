from fastapi import APIRouter, Depends, Query
from core.security import get_current_user, require_role
from core.database import get_database
from models.schemas import UserRole, NFAStatus
from typing import Dict, List
from datetime import datetime, timezone, timedelta

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: Dict = Depends(get_current_user)
):
    """Get dashboard statistics based on user role"""
    db = await get_database()
    user_id = current_user["user_id"]
    roles = current_user.get("roles", [])
    
    stats = {
        "user_info": {
            "name": current_user.get("username"),
            "roles": roles
        }
    }
    
    # Requestor stats
    if UserRole.REQUESTOR.value in roles or UserRole.SUPERADMIN.value in roles:
        total_nfas = await db.nfa_requests.count_documents({"requestor_id": user_id})
        pending_nfas = await db.nfa_requests.count_documents({
            "requestor_id": user_id,
            "status": {"$in": [NFAStatus.SECTION1_PENDING.value, NFAStatus.SECTION2_PENDING.value]}
        })
        approved_nfas = await db.nfa_requests.count_documents({
            "requestor_id": user_id,
            "status": NFAStatus.APPROVED.value
        })
        
        stats["requestor"] = {
            "total": total_nfas,
            "pending": pending_nfas,
            "approved": approved_nfas
        }
    
    # Approver stats
    if UserRole.APPROVER.value in roles or UserRole.SUPERADMIN.value in roles:
        from services.approval_service import ApprovalService
        approval_stats = await ApprovalService.get_approver_statistics(user_id)
        stats["approver"] = approval_stats
    
    # SuperAdmin stats
    if UserRole.SUPERADMIN.value in roles:
        total_users = await db.users.count_documents({})
        total_nfas_all = await db.nfa_requests.count_documents({})
        total_vendors = await db.vendors.count_documents({})
        
        stats["admin"] = {
            "total_users": total_users,
            "total_nfas": total_nfas_all,
            "total_vendors": total_vendors
        }
    
    return stats

@router.get("/nfa-analytics")
async def get_nfa_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN]))
):
    """Get NFA analytics (SuperAdmin only)"""
    db = await get_database()
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # NFAs by status
    pipeline = [
        {"$match": {"created_at": {"$gte": start_date}}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    status_counts = await db.nfa_requests.aggregate(pipeline).to_list(100)
    
    # NFAs by department
    pipeline = [
        {"$match": {"created_at": {"$gte": start_date}}},
        {"$group": {"_id": "$section1_data.department", "count": {"$sum": 1}}}
    ]
    dept_counts = await db.nfa_requests.aggregate(pipeline).to_list(100)
    
    # Average approval time
    pipeline = [
        {"$match": {"status": NFAStatus.APPROVED.value}},
        {
            "$project": {
                "approval_time": {
                    "$dateDiff": {
                        "startDate": {"$toDate": "$created_at"},
                        "endDate": {"$toDate": "$updated_at"},
                        "unit": "day"
                    }
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "avg_time": {"$avg": "$approval_time"}
            }
        }
    ]
    avg_time_result = await db.nfa_requests.aggregate(pipeline).to_list(1)
    avg_approval_time = avg_time_result[0]["avg_time"] if avg_time_result else 0
    
    return {
        "period_days": days,
        "by_status": status_counts,
        "by_department": dept_counts,
        "avg_approval_time_days": round(avg_approval_time, 2)
    }

@router.get("/approval-performance")
async def get_approval_performance(
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN]))
):
    """Get approval performance metrics (SuperAdmin only)"""
    db = await get_database()
    
    # Approver performance
    pipeline = [
        {
            "$group": {
                "_id": "$approver_id",
                "approver_name": {"$first": "$approver_name"},
                "total": {"$sum": 1},
                "approved": {
                    "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                },
                "rejected": {
                    "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}
                },
                "pending": {
                    "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                }
            }
        },
        {"$sort": {"total": -1}},
        {"$limit": 20}
    ]
    
    performance = await db.approval_workflows.aggregate(pipeline).to_list(20)
    return performance

@router.get("/vendor-analytics")
async def get_vendor_analytics(
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN, UserRole.COORDINATOR]))
):
    """Get vendor analytics"""
    db = await get_database()
    
    # Vendor usage count
    pipeline = [
        {"$match": {"section2_data.vendor_id": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": "$section2_data.vendor_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    vendor_usage = await db.nfa_requests.aggregate(pipeline).to_list(10)
    
    # Enrich with vendor names
    for item in vendor_usage:
        vendor = await db.vendors.find_one({"id": item["_id"]}, {"_id": 0, "name": 1})
        item["vendor_name"] = vendor["name"] if vendor else "Unknown"
    
    return {"top_vendors": vendor_usage}
