from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from core.database import get_database
from models.schemas import VendorCreate, VendorUpdate, VendorStatus
import logging
import uuid

logger = logging.getLogger(__name__)

class VendorService:
    @staticmethod
    async def create_vendor(vendor_data: VendorCreate) -> Dict[str, Any]:
        """Create new vendor"""
        db = await get_database()
        
        # Check if vendor name exists
        existing = await db.vendors.find_one({"name": vendor_data.name})
        if existing:
            raise ValueError("Vendor with this name already exists")
        
        vendor_doc = {
            "id": str(uuid.uuid4()),
            "name": vendor_data.name,
            "category": vendor_data.category,
            "contact_person": vendor_data.contact_person,
            "email": vendor_data.email,
            "phone": vendor_data.phone,
            "address": vendor_data.address,
            "status": VendorStatus.ACTIVE.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.vendors.insert_one(vendor_doc)
        logger.info(f"Vendor created: {vendor_data.name}")
        
        vendor_doc.pop("_id", None)
        return vendor_doc
    
    @staticmethod
    async def get_vendor_by_id(vendor_id: str) -> Optional[Dict[str, Any]]:
        """Get vendor by ID"""
        db = await get_database()
        vendor = await db.vendors.find_one({"id": vendor_id}, {"_id": 0})
        return vendor
    
    @staticmethod
    async def get_all_vendors(skip: int = 0, limit: int = 100, status: str = None) -> List[Dict[str, Any]]:
        """Get all vendors"""
        db = await get_database()
        
        query = {}
        if status:
            query["status"] = status
        
        vendors = await db.vendors.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
        return vendors
    
    @staticmethod
    async def update_vendor(vendor_id: str, vendor_data: VendorUpdate) -> Dict[str, Any]:
        """Update vendor"""
        db = await get_database()
        
        update_data = {k: v for k, v in vendor_data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.vendors.update_one(
            {"id": vendor_id},
            {"$set": update_data}
        )
        
        vendor = await db.vendors.find_one({"id": vendor_id}, {"_id": 0})
        logger.info(f"Vendor updated: {vendor_id}")
        return vendor
    
    @staticmethod
    async def delete_vendor(vendor_id: str) -> bool:
        """Delete vendor"""
        db = await get_database()
        
        result = await db.vendors.delete_one({"id": vendor_id})
        logger.info(f"Vendor deleted: {vendor_id}")
        return result.deleted_count > 0
    
    @staticmethod
    async def search_vendors(search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search vendors by name"""
        db = await get_database()
        
        vendors = await db.vendors.find(
            {
                "name": {"$regex": search_term, "$options": "i"},
                "status": VendorStatus.ACTIVE.value
            },
            {"_id": 0}
        ).limit(limit).to_list(limit)
        
        return vendors
