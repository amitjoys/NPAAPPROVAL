from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.schemas import VendorCreate, VendorUpdate, VendorResponse, UserRole
from services.vendor_service import VendorService
from core.security import get_current_user, require_role
from typing import List, Dict

router = APIRouter()

@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: VendorCreate,
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN, UserRole.COORDINATOR]))
):
    """Create new vendor (SuperAdmin/Coordinator)"""
    try:
        vendor = await VendorService.create_vendor(vendor_data)
        return vendor
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[VendorResponse])
async def get_vendors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status_filter: str = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    """Get all vendors"""
    vendors = await VendorService.get_all_vendors(skip, limit, status_filter)
    return vendors

@router.get("/search")
async def search_vendors(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """Search vendors"""
    vendors = await VendorService.search_vendors(q, limit)
    return vendors

@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get vendor by ID"""
    vendor = await VendorService.get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor

@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: str,
    vendor_data: VendorUpdate,
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN, UserRole.COORDINATOR]))
):
    """Update vendor (SuperAdmin/Coordinator)"""
    vendor = await VendorService.update_vendor(vendor_id, vendor_data)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor

@router.delete("/{vendor_id}")
async def delete_vendor(
    vendor_id: str,
    current_user: Dict = Depends(require_role([UserRole.SUPERADMIN]))
):
    """Delete vendor (SuperAdmin only)"""
    result = await VendorService.delete_vendor(vendor_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}
