from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    REQUESTOR = "requestor"
    APPROVER = "approver"
    COORDINATOR = "coordinator"
    CENTRAL_REVIEWER = "central_reviewer"
    SUPERADMIN = "superadmin"

class NFAStatus(str, Enum):
    DRAFT = "draft"
    SECTION1_PENDING = "section1_pending"
    SECTION1_APPROVED = "section1_approved"
    SECTION2_PENDING = "section2_pending"
    SECTION2_APPROVED = "section2_approved"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT_BACK = "sent_back"

class ApprovalAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    SEND_BACK = "send_back"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT_BACK = "sent_back"

class Currency(str, Enum):
    INR = "INR"
    USD = "USD"
    YEN = "YEN"

class TaxStatus(str, Enum):
    INCLUDED = "included"
    EXCLUDED = "excluded"

class VendorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# User Models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    designation: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    function: Optional[str] = None
    roles: List[UserRole] = [UserRole.REQUESTOR]

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    function: Optional[str] = None
    roles: Optional[List[UserRole]] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool = True

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# NFA Section 1 Models
class Section1Data(BaseModel):
    function_division: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    requestor_name: Optional[str] = None
    cost_code: Optional[str] = None
    subject_item: Optional[str] = None
    background_purpose: Optional[str] = None
    
    # Proposal Details
    work_approval_required: Optional[bool] = None
    proposal_description: Optional[str] = None
    activity_approved: Optional[bool] = None
    proposed_work_schedule: Optional[str] = None
    vendor_selection_required: Optional[bool] = None
    num_vendors_evaluated: Optional[int] = None
    vendor_name_proposed: Optional[str] = None
    
    # Financial Details
    budget_status: Optional[str] = None  # Budgeted/Unbudgeted
    budget_available_with_user: Optional[bool] = None
    department_with_budget: Optional[str] = None
    currency: Optional[Currency] = Currency.INR
    amount_of_approval: Optional[float] = None
    tax_status: Optional[TaxStatus] = None
    more_than_budget_amount: Optional[float] = None
    advance_payment_required: Optional[bool] = None
    advance_amount: Optional[float] = None
    security_for_advance: Optional[str] = None
    
    # Routing
    route_to: Optional[str] = None  # Vendor Selection Comm./Finance/Kanri/Purchase
    ibm_coordinator: Optional[str] = None
    approver_list: List[Dict[str, Any]] = []  # [{user_id, name, sequence}]
    
    comments: Optional[str] = None

class Section2Data(BaseModel):
    vendor_selection: Optional[bool] = None
    num_vendors_evaluated: Optional[int] = None
    vendor_name_proposed: Optional[str] = None
    vendor_id: Optional[str] = None
    comments: Optional[str] = None
    amount_of_approval: Optional[float] = None
    advance_to_be_paid: Optional[bool] = None
    advance_amount: Optional[float] = None
    security_for_advance: Optional[str] = None
    tax_status: Optional[TaxStatus] = None
    
    # Proposal Status
    proposal_status: Optional[str] = None  # submitted/approved/final_approval
    ibm_approval_nfa_number: Optional[str] = None
    ibm_approval_date: Optional[str] = None
    
    # Approvers
    approver_list: List[Dict[str, Any]] = []  # [{user_id, name, sequence, role}]

# NFA Models
class NFACreate(BaseModel):
    section1_data: Section1Data

class NFAUpdate(BaseModel):
    section1_data: Optional[Section1Data] = None
    section2_data: Optional[Section2Data] = None

class NFAResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    nfa_number: Optional[str] = None
    requestor_id: str
    requestor_name: str
    status: NFAStatus
    current_stage: str
    section1_data: Optional[Section1Data] = None
    section2_data: Optional[Section2Data] = None
    created_at: datetime
    updated_at: datetime
    pdf_url: Optional[str] = None

# Approval Models
class ApprovalWorkflowCreate(BaseModel):
    nfa_id: str
    section: int  # 1 or 2
    sequence: int
    approver_id: str
    approver_name: str
    approver_designation: str

class ApprovalActionRequest(BaseModel):
    action: ApprovalAction
    comments: Optional[str] = None

class ApprovalWorkflowResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    nfa_id: str
    section: int
    sequence: int
    approver_id: str
    approver_name: str
    approver_designation: str
    status: ApprovalStatus
    action: Optional[ApprovalAction] = None
    comments: Optional[str] = None
    action_timestamp: Optional[datetime] = None
    created_at: datetime

# Vendor Models
class VendorCreate(BaseModel):
    name: str
    category: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[VendorStatus] = None

class VendorResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    category: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: VendorStatus = VendorStatus.ACTIVE
    created_at: datetime

# Attachment Models
class AttachmentResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    nfa_id: str
    filename: str
    file_path: str
    file_size: int
    uploaded_by: str
    created_at: datetime
