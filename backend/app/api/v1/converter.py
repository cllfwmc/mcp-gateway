from fastapi import APIRouter, Depends, HTTPException
from ...core.auth import require_user
from ...schemas.protocols import ConvertRequest, ConvertResponse
from ...services.converter import ConversionService

router = APIRouter()
service = ConversionService()


@router.post("/convert", response_model=ConvertResponse)
async def convert(req: ConvertRequest, _=Depends(require_user)):
	try:
		result = await service.convert(req.source.model_dump(), req.target, req.custom_script)
		return ConvertResponse(result=result)
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))
