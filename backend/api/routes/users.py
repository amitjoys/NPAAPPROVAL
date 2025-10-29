from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.schemas import UserCreate, UserUpdate, UserResponse, UserRole
from services.auth_service import AuthService
from core.security import get_current_user, require_role, SecurityService
from core.database import get_database
from typing import List, Dict, Any
from datetime import datetime, timezone

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN, UserRole.APPROVER]))
):
    """Get all users (Admin/Approver only)"""
    db = await get_database()
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).skip(skip).limit(limit).to_list(limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get user by ID"""
    user = await AuthService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """Update user (self or SuperAdmin)"""
    # Check if user is updating self or is SuperAdmin
    if current_user["user_id"] != user_id and UserRole.SUPERADMIN.value not in current_user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    db = await get_database()
    
    update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
    
    # Handle password update
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = SecurityService.hash_password(update_data["password"])
        del update_data["password"]
    
    # Handle roles update
    if "roles" in update_data:
        update_data["roles"] = [role.value if isinstance(role, UserRole) else role for role in update_data["roles"]]
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    user = await AuthService.get_user_by_id(user_id)
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN]))
):
    """Delete user (SuperAdmin only)"""
    db = await get_database()
    result = await db.users.delete_one({"id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {"message": "User deleted successfully"}

@router.get("/search/", response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """Search users by name or email"""
    db = await get_database()
    
    users = await db.users.find(
        {
            "$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"email": {"$regex": q, "$options": "i"}},
                {"username": {"$regex": q, "$options": "i"}}
            ]
        },
        {"_id": 0, "password_hash": 0}
    ).limit(limit).to_list(limit)
    
    return users
