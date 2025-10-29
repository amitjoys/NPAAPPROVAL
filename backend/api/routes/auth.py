from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import LoginRequest, LoginResponse, UserCreate, UserResponse
from services.auth_service import AuthService
from core.security import SecurityService, get_current_user
from typing import Dict, Any

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register new user"""
    try:
        user = await AuthService.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Login user"""
    user = await AuthService.authenticate_user(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = SecurityService.create_access_token(
        data={
            "user_id": user["id"],
            "username": user["username"],
            "roles": user["roles"]
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        user=user
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user info"""
    user = await AuthService.get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
