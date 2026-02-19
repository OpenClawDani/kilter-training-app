from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
async def register():
    """Register endpoint - TBD"""
    return {"message": "register - to be implemented"}


@router.post("/login")
async def login():
    """Login endpoint - TBD"""
    return {"message": "login - to be implemented"}


@router.get("/me")
async def get_me():
    """Get current user - TBD"""
    return {"message": "get_me - to be implemented"}
