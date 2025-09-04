from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse, RedirectResponse

from .core.auth import get_current_user_optional
from .core.config import get_settings
from .api.routes import api_router


def create_app() -> FastAPI:
	settings = get_settings()
	app = FastAPI(title="MCP Gateway", version="0.1.0")

	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.cors_allow_origins,
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	app.mount("/ui", StaticFiles(directory=settings.ui_path, html=True), name="ui")

	@app.get("/")
	async def root():
		return RedirectResponse(url="/ui")

	@app.get("/health")
	async def health(_user=Depends(get_current_user_optional)):
		return JSONResponse({"status": "ok"})

	app.include_router(api_router, prefix="/api")
	return app


app = create_app()
