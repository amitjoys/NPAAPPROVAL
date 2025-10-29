import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'nfa_system')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def generate_id():
    import uuid
    return str(uuid.uuid4())

async def seed_database():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    print("🌱 Starting database seeding...")
    
    # Clear existing data
    print("🗑️  Clearing existing data...")
    await db.users.delete_many({})
    await db.vendors.delete_many({})
    await db.nfa_requests.delete_many({})
    await db.approval_workflows.delete_many({})
    await db.attachments.delete_many({})
    
    # Create Users
    print("👥 Creating users...")
    users = [
        {
            "id": generate_id(),
            "username": "superadmin",
            "email": "admin@hcil.com",
            "name": "Super Admin",
            "hashed_password": hash_password("Admin@123"),
            "designation": "System Administrator",
            "department": "IT",
            "location": "Head Office - Delhi",
            "function": "Administration",
            "roles": ["superadmin", "approver", "coordinator", "central_reviewer", "requestor"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "username": "john.doe",
            "email": "john.doe@hcil.com",
            "name": "John Doe",
            "hashed_password": hash_password("User@123"),
            "designation": "Senior Manager",
            "department": "Finance",
            "location": "Head Office - Delhi",
            "function": "Finance & Accounts",
            "roles": ["requestor", "approver"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "username": "jane.smith",
            "email": "jane.smith@hcil.com",
            "name": "Jane Smith",
            "hashed_password": hash_password("User@123"),
            "designation": "Department Head",
            "department": "Operations",
            "location": "Plant - Gurgaon",
            "function": "Manufacturing",
            "roles": ["requestor", "approver"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "username": "mike.wilson",
            "email": "mike.wilson@hcil.com",
            "name": "Mike Wilson",
            "hashed_password": hash_password("User@123"),
            "designation": "Purchase Manager",
            "department": "Purchasing",
            "location": "Head Office - Delhi",
            "function": "Procurement",
            "roles": ["coordinator", "approver"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "username": "sarah.johnson",
            "email": "sarah.johnson@hcil.com",
            "name": "Sarah Johnson",
            "hashed_password": hash_password("User@123"),
            "designation": "CFO",
            "department": "Finance",
            "location": "Head Office - Delhi",
            "function": "Finance & Accounts",
            "roles": ["central_reviewer", "approver"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "username": "raj.kumar",
            "email": "raj.kumar@hcil.com",
            "name": "Raj Kumar",
            "hashed_password": hash_password("User@123"),
            "designation": "IT Manager",
            "department": "IT",
            "location": "Head Office - Delhi",
            "function": "Information Technology",
            "roles": ["requestor"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "username": "priya.sharma",
            "email": "priya.sharma@hcil.com",
            "name": "Priya Sharma",
            "hashed_password": hash_password("User@123"),
            "designation": "HR Manager",
            "department": "HR",
            "location": "Head Office - Delhi",
            "function": "Human Resources",
            "roles": ["requestor", "approver"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.users.insert_many(users)
    print(f"✅ Created {len(users)} users")
    
    # Create Vendors
    print("🏢 Creating vendors...")
    vendors = [
        {
            "id": generate_id(),
            "name": "Tech Solutions India Pvt Ltd",
            "category": "IT Services",
            "contact_person": "Arun Verma",
            "email": "contact@techsolutions.com",
            "phone": "+91 11 4567 8900",
            "address": "Cyber City, Gurgaon, Haryana - 122002",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "name": "Global Logistics Corporation",
            "category": "Logistics & Transportation",
            "contact_person": "Vikram Singh",
            "email": "info@globallogistics.com",
            "phone": "+91 22 8765 4321",
            "address": "Andheri East, Mumbai, Maharashtra - 400069",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "name": "iManage Solutions",
            "category": "Software & OEM",
            "contact_person": "David Lee",
            "email": "sales@imanage.com",
            "phone": "+91 80 9876 5432",
            "address": "Whitefield, Bangalore, Karnataka - 560066",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "name": "Excel Manufacturing Supplies",
            "category": "Manufacturing Parts",
            "contact_person": "Ramesh Patel",
            "email": "ramesh@excelmfg.com",
            "phone": "+91 79 2345 6789",
            "address": "GIDC, Ahmedabad, Gujarat - 382424",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "name": "Green Energy Solutions",
            "category": "Energy & Utilities",
            "contact_person": "Anita Desai",
            "email": "anita@greenenergy.in",
            "phone": "+91 20 3456 7890",
            "address": "Hinjewadi, Pune, Maharashtra - 411057",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "name": "Office Supplies India",
            "category": "Office Equipment",
            "contact_person": "Suresh Kumar",
            "email": "suresh@officesupplies.in",
            "phone": "+91 11 5678 9012",
            "address": "Connaught Place, New Delhi - 110001",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": generate_id(),
            "name": "Safety Equipment Corp",
            "category": "Safety & Security",
            "contact_person": "Meena Iyer",
            "email": "meena@safetyequip.com",
            "phone": "+91 44 8901 2345",
            "address": "Guindy, Chennai, Tamil Nadu - 600032",
            "status": "inactive",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.vendors.insert_many(vendors)
    print(f"✅ Created {len(vendors)} vendors")
    
    # Create NFAs
    print("📄 Creating NFAs...")
    
    # Get some user IDs for creating NFAs
    john = next(u for u in users if u["username"] == "john.doe")
    jane = next(u for u in users if u["username"] == "jane.smith")
    raj = next(u for u in users if u["username"] == "raj.kumar")
    mike = next(u for u in users if u["username"] == "mike.wilson")
    sarah = next(u for u in users if u["username"] == "sarah.johnson")
    
    # Get vendor IDs
    tech_vendor = vendors[0]
    imanage_vendor = vendors[2]
    
    nfas = []
    
    # NFA 1 - Approved
    nfa1_id = generate_id()
    nfa1 = {
        "id": nfa1_id,
        "nfa_number": "NFA/2025/0001",
        "requestor_id": john["id"],
        "requestor_name": john["name"],
        "status": "approved",
        "current_stage": "approved",
        "section1_data": {
            "function_division": "Finance & Accounts",
            "department": "Finance",
            "location": "Head Office - Delhi",
            "requestor_name": john["name"],
            "cost_code": "FIN-2025-001",
            "subject_item": "Purchase of Financial Software License",
            "background_purpose": "We need to upgrade our financial management software to handle increased transaction volume and comply with new accounting standards. The current system is outdated and lacks automation features.",
            "work_approval_required": True,
            "proposal_description": "Procurement of Oracle Financial Suite for enterprise financial management",
            "activity_approved": True,
            "proposed_work_schedule": "Q1 2025",
            "vendor_selection_required": True,
            "num_vendors_evaluated": 3,
            "vendor_name_proposed": tech_vendor["name"],
            "budget_status": "Budgeted",
            "budget_available_with_user": True,
            "currency": "INR",
            "amount_of_approval": 2500000.00,
            "tax_status": "excluded",
            "advance_payment_required": False,
            "route_to": "Finance",
            "approver_list": [
                {"user_id": jane["id"], "name": jane["name"], "sequence": 1},
                {"user_id": sarah["id"], "name": sarah["name"], "sequence": 2}
            ]
        },
        "section2_data": {
            "vendor_selection": True,
            "num_vendors_evaluated": 3,
            "vendor_name_proposed": tech_vendor["name"],
            "vendor_id": tech_vendor["id"],
            "comments": "Tech Solutions India offers the best value with comprehensive support",
            "amount_of_approval": 2500000.00,
            "tax_status": "excluded",
            "proposal_status": "The Proposal has been approved",
            "approver_list": [
                {"user_id": mike["id"], "name": mike["name"], "sequence": 1, "role": "Coordinator"},
                {"user_id": sarah["id"], "name": sarah["name"], "sequence": 2, "role": "Central Reviewer"}
            ]
        },
        "created_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
        "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
        "pdf_url": None
    }
    nfas.append(nfa1)
    
    # NFA 2 - Section 1 Pending
    nfa2_id = generate_id()
    nfa2 = {
        "id": nfa2_id,
        "nfa_number": None,
        "requestor_id": raj["id"],
        "requestor_name": raj["name"],
        "status": "section1_pending",
        "current_stage": "section1_approval",
        "section1_data": {
            "function_division": "Information Technology",
            "department": "IT",
            "location": "Head Office - Delhi",
            "requestor_name": raj["name"],
            "cost_code": "IT-2025-012",
            "subject_item": "iManage Document Management System Renewal",
            "background_purpose": "Annual renewal of iManage DMS license. This is an OEM product essential for document management across the organization.",
            "work_approval_required": True,
            "proposal_description": "Renewal of iManage DMS subscription for 500 users",
            "activity_approved": False,
            "proposed_work_schedule": "February 2025",
            "vendor_selection_required": True,
            "num_vendors_evaluated": 1,
            "vendor_name_proposed": imanage_vendor["name"],
            "budget_status": "Budgeted",
            "budget_available_with_user": True,
            "currency": "USD",
            "amount_of_approval": 45000.00,
            "tax_status": "excluded",
            "advance_payment_required": False,
            "route_to": "Purchase",
            "comments": "iManage is a product of OEM (Adrenalin eSystems) and Hence we are renewing it from the OEM directly.",
            "approver_list": [
                {"user_id": john["id"], "name": john["name"], "sequence": 1},
                {"user_id": jane["id"], "name": jane["name"], "sequence": 2}
            ]
        },
        "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
        "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
        "pdf_url": None
    }
    nfas.append(nfa2)
    
    # NFA 3 - Section 2 Pending
    nfa3_id = generate_id()
    nfa3 = {
        "id": nfa3_id,
        "nfa_number": None,
        "requestor_id": jane["id"],
        "requestor_name": jane["name"],
        "status": "section2_pending",
        "current_stage": "section2_coordinator",
        "section1_data": {
            "function_division": "Manufacturing",
            "department": "Operations",
            "location": "Plant - Gurgaon",
            "requestor_name": jane["name"],
            "cost_code": "OPS-2025-034",
            "subject_item": "Manufacturing Equipment Maintenance",
            "background_purpose": "Annual maintenance contract for production line machinery to ensure optimal performance and prevent breakdowns.",
            "work_approval_required": True,
            "proposal_description": "Comprehensive maintenance package for 10 production line machines",
            "activity_approved": True,
            "proposed_work_schedule": "March 2025 - February 2026",
            "vendor_selection_required": True,
            "num_vendors_evaluated": 2,
            "vendor_name_proposed": vendors[3]["name"],
            "budget_status": "Budgeted",
            "budget_available_with_user": True,
            "currency": "INR",
            "amount_of_approval": 1800000.00,
            "tax_status": "excluded",
            "advance_payment_required": True,
            "advance_amount": 500000.00,
            "security_for_advance": "Bank Guarantee",
            "route_to": "Kanri",
            "approver_list": [
                {"user_id": john["id"], "name": john["name"], "sequence": 1},
                {"user_id": jane["id"], "name": jane["name"], "sequence": 2}
            ]
        },
        "created_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
        "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
        "pdf_url": None
    }
    nfas.append(nfa3)
    
    # NFA 4 - Draft
    nfa4_id = generate_id()
    nfa4 = {
        "id": nfa4_id,
        "nfa_number": None,
        "requestor_id": raj["id"],
        "requestor_name": raj["name"],
        "status": "draft",
        "current_stage": "draft",
        "section1_data": {
            "function_division": "Information Technology",
            "department": "IT",
            "location": "Head Office - Delhi",
            "requestor_name": raj["name"],
            "cost_code": "IT-2025-015",
            "subject_item": "Cloud Storage Expansion",
            "background_purpose": "Need to expand cloud storage capacity for increasing data requirements",
            "budget_status": "Budgeted",
            "currency": "INR",
            "amount_of_approval": 800000.00
        },
        "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "pdf_url": None
    }
    nfas.append(nfa4)
    
    # NFA 5 - Recently approved
    nfa5_id = generate_id()
    nfa5 = {
        "id": nfa5_id,
        "nfa_number": "NFA/2025/0002",
        "requestor_id": john["id"],
        "requestor_name": john["name"],
        "status": "approved",
        "current_stage": "approved",
        "section1_data": {
            "function_division": "Finance & Accounts",
            "department": "Finance",
            "location": "Head Office - Delhi",
            "requestor_name": john["name"],
            "cost_code": "FIN-2025-008",
            "subject_item": "Office Furniture Procurement",
            "background_purpose": "Purchase of ergonomic office furniture for new finance team members",
            "work_approval_required": True,
            "proposal_description": "50 ergonomic chairs and 25 workstations",
            "activity_approved": True,
            "proposed_work_schedule": "January 2025",
            "vendor_selection_required": True,
            "num_vendors_evaluated": 2,
            "vendor_name_proposed": vendors[5]["name"],
            "budget_status": "Budgeted",
            "budget_available_with_user": True,
            "currency": "INR",
            "amount_of_approval": 450000.00,
            "tax_status": "included",
            "advance_payment_required": False,
            "route_to": "Purchase",
            "approver_list": [
                {"user_id": jane["id"], "name": jane["name"], "sequence": 1}
            ]
        },
        "section2_data": {
            "vendor_selection": True,
            "num_vendors_evaluated": 2,
            "vendor_name_proposed": vendors[5]["name"],
            "vendor_id": vendors[5]["id"],
            "comments": "Best quality and competitive pricing",
            "amount_of_approval": 450000.00,
            "tax_status": "included",
            "proposal_status": "The Proposal has been approved",
            "approver_list": [
                {"user_id": sarah["id"], "name": sarah["name"], "sequence": 1, "role": "Central Reviewer"}
            ]
        },
        "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
        "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "pdf_url": None
    }
    nfas.append(nfa5)
    
    await db.nfa_requests.insert_many(nfas)
    print(f"✅ Created {len(nfas)} NFAs")
    
    # Create Approval Workflows
    print("✅ Creating approval workflows...")
    approvals = []
    
    # Approvals for NFA 1 (Approved)
    approvals.extend([
        {
            "id": generate_id(),
            "nfa_id": nfa1_id,
            "section": 1,
            "sequence": 1,
            "approver_id": jane["id"],
            "approver_name": jane["name"],
            "approver_designation": jane["designation"],
            "status": "approved",
            "action": "approve",
            "comments": "Approved. Good investment for our financial operations.",
            "action_timestamp": (datetime.now(timezone.utc) - timedelta(days=12)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        },
        {
            "id": generate_id(),
            "nfa_id": nfa1_id,
            "section": 1,
            "sequence": 2,
            "approver_id": sarah["id"],
            "approver_name": sarah["name"],
            "approver_designation": sarah["designation"],
            "status": "approved",
            "action": "approve",
            "comments": "Financially sound. Approved.",
            "action_timestamp": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        },
        {
            "id": generate_id(),
            "nfa_id": nfa1_id,
            "section": 2,
            "sequence": 1,
            "approver_id": mike["id"],
            "approver_name": mike["name"],
            "approver_designation": mike["designation"],
            "status": "approved",
            "action": "approve",
            "comments": "Vendor selection is appropriate.",
            "action_timestamp": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        },
        {
            "id": generate_id(),
            "nfa_id": nfa1_id,
            "section": 2,
            "sequence": 2,
            "approver_id": sarah["id"],
            "approver_name": sarah["name"],
            "approver_designation": sarah["designation"],
            "status": "approved",
            "action": "approve",
            "comments": "Final approval granted.",
            "action_timestamp": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        }
    ])
    
    # Approvals for NFA 2 (Section 1 Pending)
    approvals.extend([
        {
            "id": generate_id(),
            "nfa_id": nfa2_id,
            "section": 1,
            "sequence": 1,
            "approver_id": john["id"],
            "approver_name": john["name"],
            "approver_designation": john["designation"],
            "status": "pending",
            "action": None,
            "comments": None,
            "action_timestamp": None,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        },
        {
            "id": generate_id(),
            "nfa_id": nfa2_id,
            "section": 1,
            "sequence": 2,
            "approver_id": jane["id"],
            "approver_name": jane["name"],
            "approver_designation": jane["designation"],
            "status": "pending",
            "action": None,
            "comments": None,
            "action_timestamp": None,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        }
    ])
    
    # Approvals for NFA 3 (Section 1 approved, Section 2 pending)
    approvals.extend([
        {
            "id": generate_id(),
            "nfa_id": nfa3_id,
            "section": 1,
            "sequence": 1,
            "approver_id": john["id"],
            "approver_name": john["name"],
            "approver_designation": john["designation"],
            "status": "approved",
            "action": "approve",
            "comments": "Maintenance is necessary. Approved.",
            "action_timestamp": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        },
        {
            "id": generate_id(),
            "nfa_id": nfa3_id,
            "section": 1,
            "sequence": 2,
            "approver_id": jane["id"],
            "approver_name": jane["name"],
            "approver_designation": jane["designation"],
            "status": "approved",
            "action": "approve",
            "comments": "Approved for maintenance work.",
            "action_timestamp": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        }
    ])
    
    # Approvals for NFA 5 (Recently approved)
    approvals.extend([
        {
            "id": generate_id(),
            "nfa_id": nfa5_id,
            "section": 1,
            "sequence": 1,
            "approver_id": jane["id"],
            "approver_name": jane["name"],
            "approver_designation": jane["designation"],
            "status": "approved",
            "action": "approve",
            "comments": "Approved for furniture purchase.",
            "action_timestamp": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        },
        {
            "id": generate_id(),
            "nfa_id": nfa5_id,
            "section": 2,
            "sequence": 1,
            "approver_id": sarah["id"],
            "approver_name": sarah["name"],
            "approver_designation": sarah["designation"],
            "status": "approved",
            "action": "approve",
            "comments": "Final approval granted for furniture.",
            "action_timestamp": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
        }
    ])
    
    await db.approval_workflows.insert_many(approvals)
    print(f"✅ Created {len(approvals)} approval workflows")
    
    # Summary
    print("\n" + "="*60)
    print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n📊 Summary:")
    print(f"   • {len(users)} Users created")
    print(f"   • {len(vendors)} Vendors created")
    print(f"   • {len(nfas)} NFAs created")
    print(f"   • {len(approvals)} Approval workflows created")
    
    print("\n🔐 Login Credentials:")
    print("   Super Admin:")
    print("   • Username: superadmin")
    print("   • Password: Admin@123")
    print("\n   Regular Users:")
    print("   • Username: john.doe / jane.smith / raj.kumar / mike.wilson / sarah.johnson")
    print("   • Password: User@123")
    
    print("\n📝 Sample NFAs:")
    print("   • NFA/2025/0001 - Approved (Financial Software)")
    print("   • NFA/2025/0002 - Approved (Office Furniture)")
    print("   • Pending Approval - iManage Renewal")
    print("   • Section 2 Pending - Equipment Maintenance")
    print("   • Draft - Cloud Storage Expansion")
    
    print("\n🌐 You can now test the application!")
    print("="*60 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
