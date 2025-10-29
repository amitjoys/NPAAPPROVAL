from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from models.schemas import (
    NFACreate, NFAUpdate, NFAResponse, NFAStatus,
    Section1Data, Section2Data, UserRole
)
from services.nfa_service import NFAService
from services.auth_service import AuthService
from core.security import get_current_user
from core.database import get_database
from typing import List, Dict, Any
import aiofiles
import uuid
import os

router = APIRouter()

@router.post("/", response_model=NFAResponse, status_code=status.HTTP_201_CREATED)
async def create_nfa(
    nfa_data: NFACreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create new NFA request"""
    user = await AuthService.get_user_by_id(current_user["user_id"])
    
    nfa = await NFAService.create_nfa(
        nfa_data,
        current_user["user_id"],
        user["name"]
    )
    return nfa

@router.get("/", response_model=List[NFAResponse])
async def get_nfas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status_filter: str = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    """Get NFAs based on user role"""
    filters = {}
    
    if status_filter:
        filters["status"] = status_filter
    
    # If not SuperAdmin, show only user's NFAs
    if UserRole.SUPERADMIN.value not in current_user.get("roles", []):
        filters["requestor_id"] = current_user["user_id"]
    
    nfas = await NFAService.get_all_nfas(skip, limit, filters)
    return nfas

@router.get("/my-nfas", response_model=List[NFAResponse])
async def get_my_nfas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    current_user: Dict = Depends(get_current_user)
):
    """Get current user's NFAs"""
    nfas = await NFAService.get_nfas_by_requestor(current_user["user_id"], skip, limit)
    return nfas

@router.get("/{nfa_id}", response_model=NFAResponse)
async def get_nfa(
    nfa_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get NFA by ID"""
    nfa = await NFAService.get_nfa_by_id(nfa_id)
    
    if not nfa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NFA not found")
    
    # Check access permissions
    if (UserRole.SUPERADMIN.value not in current_user.get("roles", []) and
        nfa["requestor_id"] != current_user["user_id"]):
        # Check if user is an approver
        db = await get_database()
        approval = await db.approval_workflows.find_one({
            "nfa_id": nfa_id,
            "approver_id": current_user["user_id"]
        })
        if not approval:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return nfa

@router.post("/{nfa_id}/submit-section1")
async def submit_section1(
    nfa_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Submit Section 1 for approval"""
    nfa = await NFAService.get_nfa_by_id(nfa_id)
    
    if not nfa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NFA not found")
    
    if nfa["requestor_id"] != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if nfa["status"] != NFAStatus.DRAFT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NFA already submitted")
    
    # Get approver list from section1_data
    approvers = nfa.get("section1_data", {}).get("approver_list", [])
    if not approvers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No approvers configured")
    
    updated_nfa = await NFAService.submit_section1(nfa_id, approvers)
    
    # Send email notifications
    from tasks.email_tasks import send_approval_notification
    db = await get_database()
    
    for approver_data in approvers:
        approver = await db.users.find_one({"id": approver_data["user_id"]}, {"_id": 0})
        if approver:
            nfa_details = {
                "subject": nfa.get("section1_data", {}).get("subject_item", "N/A"),
                "requestor_name": nfa["requestor_name"],
                "department": nfa.get("section1_data", {}).get("department", "N/A"),
                "amount": nfa.get("section1_data", {}).get("amount_of_approval", 0),
                "currency": nfa.get("section1_data", {}).get("currency", "INR")
            }
            send_approval_notification.delay(nfa_id, approver["email"], approver["name"], nfa_details)
    
    return updated_nfa

@router.put("/{nfa_id}/section2", response_model=NFAResponse)
async def update_section2(
    nfa_id: str,
    section2_data: Section2Data,
    current_user: Dict = Depends(get_current_user)
):
    """Update Section 2 (Coordinator only)"""
    # Verify user is coordinator
    if UserRole.COORDINATOR.value not in current_user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only coordinators can update Section 2")
    
    nfa = await NFAService.get_nfa_by_id(nfa_id)
    
    if not nfa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NFA not found")
    
    if nfa["status"] != NFAStatus.SECTION1_APPROVED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Section 1 not yet approved")
    
    updated_nfa = await NFAService.update_section2(nfa_id, section2_data, current_user["user_id"])
    return updated_nfa

@router.post("/{nfa_id}/submit-section2")
async def submit_section2(
    nfa_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Submit Section 2 for approval (Coordinator only)"""
    if UserRole.COORDINATOR.value not in current_user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only coordinators can submit Section 2")
    
    nfa = await NFAService.get_nfa_by_id(nfa_id)
    
    if not nfa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NFA not found")
    
    # Get approver list from section2_data
    approvers = nfa.get("section2_data", {}).get("approver_list", [])
    if not approvers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No approvers configured")
    
    updated_nfa = await NFAService.submit_section2(nfa_id, approvers)
    
    # Send email notifications
    from tasks.email_tasks import send_approval_notification
    db = await get_database()
    
    for approver_data in approvers:
        approver = await db.users.find_one({"id": approver_data["user_id"]}, {"_id": 0})
        if approver:
            nfa_details = {
                "subject": nfa.get("section1_data", {}).get("subject_item", "N/A"),
                "requestor_name": nfa["requestor_name"],
                "department": nfa.get("section1_data", {}).get("department", "N/A"),
                "amount": nfa.get("section2_data", {}).get("amount_of_approval", 0),
                "currency": nfa.get("section1_data", {}).get("currency", "INR")
            }
            send_approval_notification.delay(nfa_id, approver["email"], approver["name"], nfa_details)
    
    return updated_nfa

@router.post("/{nfa_id}/upload")
async def upload_attachment(
    nfa_id: str,
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
):
    """Upload attachment to NFA"""
    nfa = await NFAService.get_nfa_by_id(nfa_id)
    
    if not nfa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NFA not found")
    
    # Create upload directory
    upload_dir = "/app/backend/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Save attachment record
    db = await get_database()
    attachment_doc = {
        "id": str(uuid.uuid4()),
        "nfa_id": nfa_id,
        "filename": file.filename,
        "file_path": file_path,
        "file_size": len(content),
        "uploaded_by": current_user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.attachments.insert_one(attachment_doc)
    attachment_doc.pop("_id", None)
    
    return attachment_doc

@router.get("/{nfa_id}/attachments")
async def get_attachments(
    nfa_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get attachments for NFA"""
    db = await get_database()
    attachments = await db.attachments.find({"nfa_id": nfa_id}, {"_id": 0}).to_list(100)
    return attachments

@router.delete("/{nfa_id}")
async def delete_nfa(
    nfa_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete NFA (SuperAdmin only)"""
    if UserRole.SUPERADMIN.value not in current_user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin can delete NFAs")
    
    result = await NFAService.delete_nfa(nfa_id)
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NFA not found")
    
    return {"message": "NFA deleted successfully"}

from datetime import datetime, timezone
