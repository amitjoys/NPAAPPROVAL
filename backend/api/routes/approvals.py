from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.schemas import ApprovalActionRequest, ApprovalWorkflowResponse, ApprovalAction, UserRole
from services.approval_service import ApprovalService
from core.security import get_current_user
from typing import List, Dict

router = APIRouter()

@router.get("/pending", response_model=List[ApprovalWorkflowResponse])
async def get_pending_approvals(
    current_user: Dict = Depends(get_current_user)
):
    """Get pending approvals for current user"""
    approvals = await ApprovalService.get_pending_approvals(current_user["user_id"])
    return approvals

@router.get("/statistics")
async def get_approval_statistics(
    current_user: Dict = Depends(get_current_user)
):
    """Get approval statistics for current user"""
    stats = await ApprovalService.get_approver_statistics(current_user["user_id"])
    return stats

@router.get("/nfa/{nfa_id}/history", response_model=List[ApprovalWorkflowResponse])
async def get_approval_history(
    nfa_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get approval history for an NFA"""
    history = await ApprovalService.get_approval_history(nfa_id)
    return history

@router.post("/{workflow_id}/action")
async def process_approval(
    workflow_id: str,
    action_request: ApprovalActionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Process approval action (approve/reject/send_back)"""
    try:
        result = await ApprovalService.process_approval(
            workflow_id,
            current_user["user_id"],
            action_request.action,
            action_request.comments
        )
        
        # Emit WebSocket event
        from api.routes.websocket import manager
        await manager.broadcast({
            "type": "approval_action",
            "workflow_id": workflow_id,
            "nfa_id": result["nfa_id"],
            "action": action_request.action.value,
            "approver": current_user.get("username")
        })
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
