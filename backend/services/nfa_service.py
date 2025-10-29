from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from core.database import get_database
from models.schemas import (
    NFACreate, NFAUpdate, NFAStatus, Section1Data, Section2Data,
    ApprovalStatus, ApprovalAction
)
import logging
import uuid

logger = logging.getLogger(__name__)

class NFAService:
    @staticmethod
    async def create_nfa(nfa_data: NFACreate, requestor_id: str, requestor_name: str) -> Dict[str, Any]:
        """Create new NFA request"""
        db = await get_database()
        
        nfa_doc = {
            "id": str(uuid.uuid4()),
            "nfa_number": None,  # Generated on final approval
            "requestor_id": requestor_id,
            "requestor_name": requestor_name,
            "status": NFAStatus.DRAFT.value,
            "current_stage": "draft",
            "section1_data": nfa_data.section1_data.model_dump() if nfa_data.section1_data else {},
            "section2_data": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "pdf_url": None
        }
        
        await db.nfa_requests.insert_one(nfa_doc)
        logger.info(f"NFA created: {nfa_doc['id']} by {requestor_name}")
        
        nfa_doc.pop("_id", None)
        return nfa_doc
    
    @staticmethod
    async def submit_section1(nfa_id: str, approvers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Submit Section 1 for approval"""
        db = await get_database()
        
        # Update NFA status
        await db.nfa_requests.update_one(
            {"id": nfa_id},
            {
                "$set": {
                    "status": NFAStatus.SECTION1_PENDING.value,
                    "current_stage": "section1_approval",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Create approval workflows
        from services.approval_service import ApprovalService
        await ApprovalService.create_approval_workflows(nfa_id, 1, approvers)
        
        # Get updated NFA
        nfa = await db.nfa_requests.find_one({"id": nfa_id}, {"_id": 0})
        logger.info(f"Section 1 submitted for NFA: {nfa_id}")
        
        return nfa
    
    @staticmethod
    async def update_section2(nfa_id: str, section2_data: Section2Data, coordinator_id: str) -> Dict[str, Any]:
        """Update Section 2 data"""
        db = await get_database()
        
        await db.nfa_requests.update_one(
            {"id": nfa_id},
            {
                "$set": {
                    "section2_data": section2_data.model_dump(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        nfa = await db.nfa_requests.find_one({"id": nfa_id}, {"_id": 0})
        logger.info(f"Section 2 updated for NFA: {nfa_id}")
        return nfa
    
    @staticmethod
    async def submit_section2(nfa_id: str, approvers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Submit Section 2 for approval"""
        db = await get_database()
        
        await db.nfa_requests.update_one(
            {"id": nfa_id},
            {
                "$set": {
                    "status": NFAStatus.SECTION2_PENDING.value,
                    "current_stage": "section2_approval",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Create Section 2 approval workflows
        from services.approval_service import ApprovalService
        await ApprovalService.create_approval_workflows(nfa_id, 2, approvers)
        
        nfa = await db.nfa_requests.find_one({"id": nfa_id}, {"_id": 0})
        logger.info(f"Section 2 submitted for NFA: {nfa_id}")
        return nfa
    
    @staticmethod
    async def get_nfa_by_id(nfa_id: str) -> Optional[Dict[str, Any]]:
        """Get NFA by ID"""
        db = await get_database()
        nfa = await db.nfa_requests.find_one({"id": nfa_id}, {"_id": 0})
        return nfa
    
    @staticmethod
    async def get_nfas_by_requestor(requestor_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get NFAs by requestor"""
        db = await get_database()
        cursor = db.nfa_requests.find(
            {"requestor_id": requestor_id},
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        nfas = await cursor.to_list(length=limit)
        return nfas
    
    @staticmethod
    async def get_all_nfas(skip: int = 0, limit: int = 100, filters: Dict = None) -> List[Dict[str, Any]]:
        """Get all NFAs with optional filters"""
        db = await get_database()
        
        query = filters or {}
        cursor = db.nfa_requests.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        
        nfas = await cursor.to_list(length=limit)
        return nfas
    
    @staticmethod
    async def update_nfa_status(nfa_id: str, status: NFAStatus, stage: str = None) -> Dict[str, Any]:
        """Update NFA status"""
        db = await get_database()
        
        update_data = {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if stage:
            update_data["current_stage"] = stage
        
        await db.nfa_requests.update_one(
            {"id": nfa_id},
            {"$set": update_data}
        )
        
        nfa = await db.nfa_requests.find_one({"id": nfa_id}, {"_id": 0})
        return nfa
    
    @staticmethod
    async def generate_nfa_number() -> str:
        """Generate unique NFA number"""
        db = await get_database()
        
        # Get current year
        year = datetime.now(timezone.utc).year
        
        # Find the highest NFA number for current year
        pipeline = [
            {"$match": {"nfa_number": {"$regex": f"^NFA/{year}/"}}},
            {"$project": {"number": {"$toInt": {"$arrayElemAt": [{"$split": ["$nfa_number", "/"]}, 2]}}}},
            {"$sort": {"number": -1}},
            {"$limit": 1}
        ]
        
        result = await db.nfa_requests.aggregate(pipeline).to_list(1)
        
        if result:
            next_number = result[0]["number"] + 1
        else:
            next_number = 1
        
        nfa_number = f"NFA/{year}/{next_number:04d}"
        logger.info(f"Generated NFA number: {nfa_number}")
        return nfa_number
    
    @staticmethod
    async def finalize_nfa(nfa_id: str, pdf_url: str) -> Dict[str, Any]:
        """Finalize NFA with number and PDF"""
        db = await get_database()
        
        nfa_number = await NFAService.generate_nfa_number()
        
        await db.nfa_requests.update_one(
            {"id": nfa_id},
            {
                "$set": {
                    "nfa_number": nfa_number,
                    "status": NFAStatus.APPROVED.value,
                    "current_stage": "completed",
                    "pdf_url": pdf_url,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        nfa = await db.nfa_requests.find_one({"id": nfa_id}, {"_id": 0})
        logger.info(f"NFA finalized: {nfa_number}")
        return nfa
    
    @staticmethod
    async def delete_nfa(nfa_id: str) -> bool:
        """Delete NFA (SuperAdmin only)"""
        db = await get_database()
        
        # Delete NFA
        result = await db.nfa_requests.delete_one({"id": nfa_id})
        
        # Delete associated approvals
        await db.approval_workflows.delete_many({"nfa_id": nfa_id})
        
        # Delete attachments
        await db.attachments.delete_many({"nfa_id": nfa_id})
        
        logger.info(f"NFA deleted: {nfa_id}")
        return result.deleted_count > 0
