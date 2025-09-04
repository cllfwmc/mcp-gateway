from fastapi import APIRouter
from .v1.adapters import router as adapters_router
from .v1.mcp import router as mcp_router
from .v1.converter import router as converter_router

api_router = APIRouter()
api_router.include_router(mcp_router, prefix="/v1/mcp", tags=["mcp"])
api_router.include_router(adapters_router, prefix="/v1/adapters", tags=["adapters"])
api_router.include_router(converter_router, prefix="/v1/converter", tags=["converter"])
