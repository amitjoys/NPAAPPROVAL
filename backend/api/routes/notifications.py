from fastapi import APIRouter, Depends
from core.security import get_current_user
from core.database import get_database
from typing import Dict, List
from datetime import datetime, timezone, timedelta

router = APIRouter()

@router.get("/unread")
async def get_unread_notifications(
    current_user: Dict = Depends(get_current_user)
):
    """Get unread notifications for current user"""
    db = await get_database()
    user_id = current_user["user_id"]
    
    # Get pending approvals as notifications
    approvals = await db.approval_workflows.find({
        "approver_id": user_id,
        "status": "pending"
    }).to_list(10)
    
    notifications = []
    for approval in approvals:
        # Get NFA details
        nfa = await db.nfa_requests.find_one({"id": approval["nfa_id"]})
        if nfa:
            notifications.append({
                "title": "Approval Required",
                "message": f"NFA {nfa.get('nfa_number', approval['nfa_id'][:8])} needs your approval",
                "time": "Just now",
                "type": "approval",
                "nfa_id": approval["nfa_id"]
            })
    
    return notifications

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Mark a notification as read"""
    # This would mark a notification as read in the database
    return {"status": "success"}

@router.get("/")
async def get_all_notifications(
    current_user: Dict = Depends(get_current_user),
    limit: int = 50
):
    """Get all notifications for current user"""
    db = await get_database()
    user_id = current_user["user_id"]
    
    # Get all approvals (both pending and completed)
    approvals = await db.approval_workflows.find({
        "approver_id": user_id
    }).sort("created_at", -1).limit(limit).to_list(limit)
    
    notifications = []
    for approval in approvals:
        # Get NFA details
        nfa = await db.nfa_requests.find_one({"id": approval["nfa_id"]})
        if nfa:
            if approval["status"] == "pending":
                title = "Approval Required"
                message = f"NFA {nfa.get('nfa_number', approval['nfa_id'][:8])} needs your approval"
            elif approval["status"] == "approved":
                title = "Approval Completed"
                message = f"You approved NFA {nfa.get('nfa_number', approval['nfa_id'][:8])}"
            else:
                title = "Approval Action"
                message = f"Action taken on NFA {nfa.get('nfa_number', approval['nfa_id'][:8])}"
                
            # Calculate relative time
            created_at = datetime.fromisoformat(approval.get("created_at", datetime.now(timezone.utc).isoformat()))
            now = datetime.now(timezone.utc)
            delta = now - created_at
            
            if delta.days > 0:
                time_str = f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                time_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif delta.seconds > 60:
                minutes = delta.seconds // 60
                time_str = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                time_str = "Just now"
                
            notifications.append({
                "id": approval.get("id", ""),
                "title": title,
                "message": message,
                "time": time_str,
                "type": "approval",
                "nfa_id": approval["nfa_id"],
                "read": approval["status"] != "pending"
            })
    
    return notifications
