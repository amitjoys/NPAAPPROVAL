from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from core.database import get_database
from models.schemas import ApprovalStatus, ApprovalAction, NFAStatus
import logging
import uuid

logger = logging.getLogger(__name__)

class ApprovalService:
    @staticmethod
    async def create_approval_workflows(
        nfa_id: str,
        section: int,
        approvers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create approval workflows for a section"""
        db = await get_database()
        
        workflows = []
        for approver in approvers:
            workflow_doc = {
                "id": str(uuid.uuid4()),
                "nfa_id": nfa_id,
                "section": section,
                "sequence": approver.get("sequence", 0),
                "approver_id": approver["user_id"],
                "approver_name": approver["name"],
                "approver_designation": approver.get("designation", ""),
                "status": ApprovalStatus.PENDING.value,
                "action": None,
                "comments": None,
                "action_timestamp": None,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            workflows.append(workflow_doc)
        
        if workflows:
            await db.approval_workflows.insert_many(workflows)
            logger.info(f"Created {len(workflows)} approval workflows for NFA: {nfa_id}, Section: {section}")
        
        return workflows
    
    @staticmethod
    async def process_approval(
        workflow_id: str,
        approver_id: str,
        action: ApprovalAction,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process approval action"""
        db = await get_database()
        
        # Get workflow
        workflow = await db.approval_workflows.find_one({"id": workflow_id})
        if not workflow:
            raise ValueError("Approval workflow not found")
        
        # Verify approver
        if workflow["approver_id"] != approver_id:
            raise ValueError("Unauthorized: You are not the designated approver")
        
        # Check if already processed
        if workflow["status"] != ApprovalStatus.PENDING.value:
            raise ValueError("This approval has already been processed")
        
        # Update workflow
        new_status = {
            ApprovalAction.APPROVE: ApprovalStatus.APPROVED,
            ApprovalAction.REJECT: ApprovalStatus.REJECTED,
            ApprovalAction.SEND_BACK: ApprovalStatus.SENT_BACK
        }[action]
        
        await db.approval_workflows.update_one(
            {"id": workflow_id},
            {
                "$set": {
                    "status": new_status.value,
                    "action": action.value,
                    "comments": comments,
                    "action_timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        logger.info(f"Approval processed: {workflow_id}, Action: {action.value}")
        
        # Handle workflow progression
        nfa_id = workflow["nfa_id"]
        section = workflow["section"]
        
        if action == ApprovalAction.REJECT or action == ApprovalAction.SEND_BACK:
            # Update NFA status
            from services.nfa_service import NFAService
            nfa_status = NFAStatus.REJECTED if action == ApprovalAction.REJECT else NFAStatus.SENT_BACK
            await NFAService.update_nfa_status(nfa_id, nfa_status, "rejected" if action == ApprovalAction.REJECT else "sent_back")
        elif action == ApprovalAction.APPROVE:
            # Check if all approvals in section are complete
            await ApprovalService.check_section_completion(nfa_id, section)
        
        # Get updated workflow
        updated_workflow = await db.approval_workflows.find_one({"id": workflow_id}, {"_id": 0})
        return updated_workflow
    
    @staticmethod
    async def check_section_completion(nfa_id: str, section: int):
        """Check if all approvals in a section are complete"""
        db = await get_database()
        
        # Get all workflows for this section
        workflows = await db.approval_workflows.find(
            {"nfa_id": nfa_id, "section": section},
            {"_id": 0}
        ).sort("sequence", 1).to_list(100)
        
        # Check if all are approved
        all_approved = all(w["status"] == ApprovalStatus.APPROVED.value for w in workflows)
        
        if all_approved:
            from services.nfa_service import NFAService
            
            if section == 1:
                # Section 1 complete - move to coordinator stage
                await NFAService.update_nfa_status(
                    nfa_id,
                    NFAStatus.SECTION1_APPROVED,
                    "coordinator_processing"
                )
                logger.info(f"Section 1 approvals complete for NFA: {nfa_id}")
                
                # Notify coordinator
                from tasks.email_tasks import send_coordinator_notification
                nfa = await NFAService.get_nfa_by_id(nfa_id)
                if nfa and nfa.get("section1_data", {}).get("ibm_coordinator"):
                    send_coordinator_notification.delay(nfa_id, nfa["section1_data"]["ibm_coordinator"])
            
            elif section == 2:
                # Section 2 complete - finalize NFA
                logger.info(f"Section 2 approvals complete for NFA: {nfa_id}")
                
                # Generate PDF and finalize
                from tasks.pdf_tasks import generate_nfa_pdf
                generate_nfa_pdf.delay(nfa_id)
    
    @staticmethod
    async def get_pending_approvals(approver_id: str) -> List[Dict[str, Any]]:
        """Get pending approvals for an approver"""
        db = await get_database()
        
        workflows = await db.approval_workflows.find(
            {
                "approver_id": approver_id,
                "status": ApprovalStatus.PENDING.value
            },
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)
        
        # Enrich with NFA data
        for workflow in workflows:
            nfa = await db.nfa_requests.find_one({"id": workflow["nfa_id"]}, {"_id": 0})
            if nfa:
                workflow["nfa"] = nfa
        
        return workflows
    
    @staticmethod
    async def get_approval_history(nfa_id: str) -> List[Dict[str, Any]]:
        """Get approval history for an NFA"""
        db = await get_database()
        
        workflows = await db.approval_workflows.find(
            {"nfa_id": nfa_id},
            {"_id": 0}
        ).sort([("section", 1), ("sequence", 1)]).to_list(100)
        
        return workflows
    
    @staticmethod
    async def get_approver_statistics(approver_id: str) -> Dict[str, Any]:
        """Get approval statistics for an approver"""
        db = await get_database()
        
        total = await db.approval_workflows.count_documents({"approver_id": approver_id})
        pending = await db.approval_workflows.count_documents({
            "approver_id": approver_id,
            "status": ApprovalStatus.PENDING.value
        })
        approved = await db.approval_workflows.count_documents({
            "approver_id": approver_id,
            "status": ApprovalStatus.APPROVED.value
        })
        rejected = await db.approval_workflows.count_documents({
            "approver_id": approver_id,
            "status": ApprovalStatus.REJECTED.value
        })
        
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected
        }
