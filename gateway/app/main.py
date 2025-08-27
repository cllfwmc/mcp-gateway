from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .config import ConfigLoader
from .routers.mcp import router as mcp_router
from .routers.sse import router as sse_router

app = FastAPI(title="MCP Gateway", version="0.1.0")

# Templates (Tailwind via CDN, no local static required yet)
templates = Jinja2Templates(directory="gateway/app/templates")

# Routers
app.include_router(mcp_router, prefix="")
app.include_router(sse_router, prefix="")


@app.get("/health", response_class=JSONResponse)
async def health() -> dict:
    cfg = ConfigLoader.get()
    return {"status": "ok", "servers": list(cfg.mcp_servers.keys())}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    cfg = ConfigLoader.get()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "MCP Gateway", "servers": cfg.mcp_servers},
    )
