from fastapi import APIRouter

router = APIRouter()


@router.post("/upload")
async def upload_video():
    """Upload video - TBD"""
    return {"message": "upload - to be implemented"}


@router.get("/{video_id}")
async def get_video(video_id: str):
    """Get video status - TBD"""
    return {"video_id": video_id, "message": "status - to be implemented"}
