import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from core.security import SecurityService
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

async def seed_database():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🌱 Starting database seeding...")
    
    # Clear existing data (except superadmin)
    print("📦 Clearing existing data...")
    await db.users.delete_many({"username": {"$ne": "superadmin"}})
    await db.vendors.delete_many({})
    await db.nfa_requests.delete_many({})
    await db.approval_workflows.delete_many({})
    await db.attachments.delete_many({})
    
    # Seed Users
    print("👥 Creating users...")
    users = [
        {
            "id": "user_001",
            "username": "john.doe",
            "email": "john.doe@hcil.com",
            "password_hash": SecurityService.hash_password("password123"),
            "name": "John Doe",
            "designation": "Manager",
            "department": "Finance",
            "location": "Gurgaon",
            "function": "Financial Planning",
            "roles": ["requestor", "approver"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "user_002",
            "username": "jane.smith",
            "email": "jane.smith@hcil.com",
            "password_hash": SecurityService.hash_password("password123"),
            "name": "Jane Smith",
            "designation": "Senior Manager",
            "department": "Purchasing",
            "location": "Gurgaon",
            "function": "Procurement",
            "roles": ["requestor", "approver", "coordinator"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "user_003",
            "username": "robert.johnson",
            "email": "robert.johnson@hcil.com",
            "password_hash": SecurityService.hash_password("password123"),
            "name": "Robert Johnson",
            "designation": "Department Head",
            "department": "IT",
            "location": "Gurgaon",
            "function": "Information Technology",
            "roles": ["requestor", "approver"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "user_004",
            "username": "maria.garcia",
            "email": "maria.garcia@hcil.com",
            "password_hash": SecurityService.hash_password("password123"),
            "name": "Maria Garcia",
            "designation": "IBM Coordinator",
            "department": "Vendor Management",
            "location": "Gurgaon",
            "function": "Vendor Relations",
            "roles": ["coordinator"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "user_005",
            "username": "david.lee",
            "email": "david.lee@hcil.com",
            "password_hash": SecurityService.hash_password("password123"),
            "name": "David Lee",
            "designation": "Chief Financial Officer",
            "department": "Finance",
            "location": "Gurgaon",
            "function": "Executive",
            "roles": ["approver", "central_reviewer"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "user_006",
            "username": "sarah.wilson",
            "email": "sarah.wilson@hcil.com",
            "password_hash": SecurityService.hash_password("password123"),
            "name": "Sarah Wilson",
            "designation": "Associate",
            "department": "Marketing",
            "location": "Delhi",
            "function": "Brand Management",
            "roles": ["requestor"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.users.insert_many(users)
    print(f"✅ Created {len(users)} users")
    
    # Seed Vendors
    print("🏢 Creating vendors...")
    vendors = [
        {
            "id": "vendor_001",
            "name": "Adrenalin eSystems Ltd.",
            "category": "Software & IT Services",
            "contact_person": "Raj Kumar",
            "email": "raj@adrenalin.com",
            "phone": "+91-9876543210",
            "address": "Bangalore, Karnataka",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "vendor_002",
            "name": "TCS InfoTech Solutions",
            "category": "IT Consulting",
            "contact_person": "Priya Sharma",
            "email": "priya@tcs.com",
            "phone": "+91-9876543211",
            "address": "Mumbai, Maharashtra",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "vendor_003",
            "name": "ABC Manufacturing Co.",
            "category": "Manufacturing",
            "contact_person": "Amit Patel",
            "email": "amit@abc.com",
            "phone": "+91-9876543212",
            "address": "Pune, Maharashtra",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "vendor_004",
            "name": "Global Logistics Ltd.",
            "category": "Logistics & Transport",
            "contact_person": "Suresh Reddy",
            "email": "suresh@global-logistics.com",
            "phone": "+91-9876543213",
            "address": "Hyderabad, Telangana",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "vendor_005",
            "name": "Premium Office Supplies",
            "category": "Office Equipment",
            "contact_person": "Neha Gupta",
            "email": "neha@premium-office.com",
            "phone": "+91-9876543214",
            "address": "Gurgaon, Haryana",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.vendors.insert_many(vendors)
    print(f"✅ Created {len(vendors)} vendors")
    
    print("\n✨ Database seeding completed successfully!")
    print("\n📋 Demo Credentials:")
    print("=" * 50)
    print("SuperAdmin:")
    print("  Username: superadmin")
    print("  Password: Admin@123")
    print("\nRegular Users (all with password: password123):")
    for user in users:
        roles_str = ", ".join(user['roles'])
        print(f"  {user['username']:20} - {user['designation']:25} [{roles_str}]")
    print("=" * 50)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
