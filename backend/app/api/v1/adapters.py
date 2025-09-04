from fastapi import APIRouter, Depends
from ...core.auth import require_user

router = APIRouter()


@router.get("/templates")
async def list_templates(_=Depends(require_user)):
	return {
		"protocols": [
			{"name": "streamable-http", "path": "/configs/streamable-http.json"},
			{"name": "sse", "path": "/configs/sse.json"},
			{"name": "stdio", "path": "/configs/stdio.json"},
		]
	}


@router.post("/convert")
async def convert_protocol(_: dict, _user=Depends(require_user)):
	# Placeholder: will route to adapter based on input
	return {"status": "queued"}
