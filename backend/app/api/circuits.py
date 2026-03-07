from fastapi import APIRouter

router = APIRouter()


@router.get("/{circuit_id}")
async def get_circuit(circuit_id: str):
    """Get circuit details - TBD"""
    return {"circuit_id": circuit_id, "message": "circuit - to be implemented"}
