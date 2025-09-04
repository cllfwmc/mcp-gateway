from fastapi import APIRouter, Depends
from ...core.auth import require_user

router = APIRouter()


@router.get("/registry")
async def get_registry(_=Depends(require_user)):
	return {"items": []}


@router.get("/heartbeat")
async def heartbeat(_=Depends(require_user)):
	return {"ok": True}


@router.get("/tools")
async def list_tools(_=Depends(require_user)):
	return {"count": 0, "tools": []}


@router.get("/tools/{tool_id}")
async def tool_detail(tool_id: str, _=Depends(require_user)):
	return {"id": tool_id, "detail": {}}
