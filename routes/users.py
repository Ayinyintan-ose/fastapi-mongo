from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from models.users import UserRegistration, UserResponse, UserLogin
from utils.security import hash_password, verify_password
from utils.jwt_handler import access_token, verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["doc_management"] 
user_collection = db["users"]

router = APIRouter(prefix="/users", tags=["Users"])
bearer_scheme = HTTPBearer()

async def current_user(token: str = Depends(bearer_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalid or expired")
    return payload

async def admin_access(user=Depends(current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access to admin only")
    return user

@router.post("/auth/register", response_model=dict)
async def register(user: UserRegistration):
    try:
        print(f"Received password: {user.password!r}, Byte length: {len(user.password.encode('utf-8'))}")
        
        password_bytes = user.password.encode("utf-8")
        if len(password_bytes) > 72:
            raise HTTPException(
                status_code=400,
                detail="Password is too long (max 72 bytes). Please use a shorter password."
            )

        existing_user = await user_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email is already registered")

        hashed_pw = hash_password(user.password)

        user_doc = {
            "username": user.username,
            "email": user.email,
            "password": hashed_pw,
            "role": "user",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        result = await user_collection.insert_one(user_doc)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to insert user")

        return {"message": "User registered successfully!", "id": str(result.inserted_id)}

    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    
@router.post("/auth/login")
async def login(user: UserLogin):
    db_user = await user_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = access_token(  
        data = {"id": str(db_user["_id"]), "role": db_user["role"]},
        expires = timedelta(minutes=30)
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_profile(user=Depends(current_user)):
    try:
        db_user = await user_collection.find_one({"_id": ObjectId(user["id"])})
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(
            id=str(db_user["_id"]),
            username=db_user["username"],
            email=db_user["email"],
            role=db_user["role"],
            created_at=db_user["created_at"],
            updated_at=db_user["updated_at"],
        )

    except Exception as e:
        print(f"Profile fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")

@router.get("/", dependencies=[Depends(admin_access)])
async def get_all_users():
    try:
        users = []
        async for user in user_collection.find():
            user["_id"] = str(user["_id"])
            del user["password"]  
            users.append(user)
        return users

    except Exception as e:
        print(f"Get users error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.put("/{id}", dependencies=[Depends(admin_access)])
async def update_user(id: str, data: dict):
    try:
        result = await user_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data, "$currentDate": {"updated_at": True}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User updated"}

    except Exception as e:
        print(f"Update user error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.delete("/{id}", dependencies=[Depends(admin_access)])
async def delete_user(id: str):
    try:
        result = await user_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted"}

    except Exception as e:
        print(f"Delete user error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

