from __future__ import annotations
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from ..config import ConfigLoader, MCPServer

router = APIRouter()


class ServerCreateRequest(BaseModel):
    name: str
    type: str
    url: str
    headers: Dict[str, str] | None = None
    requestTransform: str | None = None
    responseTransform: str | None = None


class ServerUpdateRequest(BaseModel):
    type: str | None = None
    url: str | None = None
    headers: Dict[str, str] | None = None
    requestTransform: str | None = None
    responseTransform: str | None = None


class ServerResponse(BaseModel):
    name: str
    type: str
    url: str
    headers: Dict[str, str] | None = None
    requestTransform: str | None = None
    responseTransform: str | None = None
    toolsCount: int = 0


class ToolInfo(BaseModel):
    name: str
    description: str | None = None
    inputSchema: Dict | None = None


class ServerToolsResponse(BaseModel):
    name: str
    tools: List[ToolInfo]


async def get_server_tools(server: MCPServer) -> List[ToolInfo]:
    """Get tools list from MCP server"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            resp = await client.post(
                server.url, 
                json=payload, 
                headers=server.headers or {}
            )
            resp.raise_for_status()
            result = resp.json()
            
            if "result" in result and "tools" in result["result"]:
                tools = []
                for tool in result["result"]["tools"]:
                    tools.append(ToolInfo(
                        name=tool.get("name", ""),
                        description=tool.get("description"),
                        inputSchema=tool.get("inputSchema")
                    ))
                return tools
            return []
    except Exception as e:
        print(f"Error getting tools from {server.url}: {e}")
        return []


@router.get("/admin/servers", response_model=List[ServerResponse])
async def list_servers() -> List[ServerResponse]:
    cfg = ConfigLoader.get()
    servers = []
    
    for name, server in cfg.mcp_servers.items():
        tools = await get_server_tools(server)
        servers.append(ServerResponse(
            name=name,
            type=server.type,
            url=server.url,
            headers=server.headers,
            requestTransform=server.requestTransform,
            responseTransform=server.responseTransform,
            toolsCount=len(tools)
        ))
    
    return servers


@router.get("/admin/servers/{name}", response_model=ServerResponse)
async def get_server(name: str) -> ServerResponse:
    cfg = ConfigLoader.get()
    if name not in cfg.mcp_servers:
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found")
    
    server = cfg.mcp_servers[name]
    tools = await get_server_tools(server)
    
    return ServerResponse(
        name=name,
        type=server.type,
        url=server.url,
        headers=server.headers,
        requestTransform=server.requestTransform,
        responseTransform=server.responseTransform,
        toolsCount=len(tools)
    )


@router.get("/admin/servers/{name}/tools", response_model=ServerToolsResponse)
async def get_server_tools_endpoint(name: str) -> ServerToolsResponse:
    cfg = ConfigLoader.get()
    if name not in cfg.mcp_servers:
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found")
    
    server = cfg.mcp_servers[name]
    tools = await get_server_tools(server)
    
    return ServerToolsResponse(
        name=name,
        tools=tools
    )


@router.post("/admin/servers", response_model=ServerResponse)
async def create_server(request: ServerCreateRequest) -> ServerResponse:
    cfg = ConfigLoader.get()
    if request.name in cfg.mcp_servers:
        raise HTTPException(status_code=409, detail=f"Server '{request.name}' already exists")
    
    server = MCPServer(
        type=request.type,
        url=request.url,
        headers=request.headers,
        requestTransform=request.requestTransform,
        responseTransform=request.responseTransform
    )
    
    ConfigLoader.add_server(request.name, server)
    
    tools = await get_server_tools(server)
    
    return ServerResponse(
        name=request.name,
        type=server.type,
        url=server.url,
        headers=server.headers,
        requestTransform=server.requestTransform,
        responseTransform=server.responseTransform,
        toolsCount=len(tools)
    )


@router.put("/admin/servers/{name}", response_model=ServerResponse)
async def update_server(name: str, request: ServerUpdateRequest) -> ServerResponse:
    cfg = ConfigLoader.get()
    if name not in cfg.mcp_servers:
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found")
    
    current_server = cfg.mcp_servers[name]
    
    # Update only provided fields
    update_data = {}
    if request.type is not None:
        update_data["type"] = request.type
    if request.url is not None:
        update_data["url"] = request.url
    if request.headers is not None:
        update_data["headers"] = request.headers
    if request.requestTransform is not None:
        update_data["requestTransform"] = request.requestTransform
    if request.responseTransform is not None:
        update_data["responseTransform"] = request.responseTransform
    
    server = MCPServer(
        type=update_data.get("type", current_server.type),
        url=update_data.get("url", current_server.url),
        headers=update_data.get("headers", current_server.headers),
        requestTransform=update_data.get("requestTransform", current_server.requestTransform),
        responseTransform=update_data.get("responseTransform", current_server.responseTransform)
    )
    
    ConfigLoader.update_server(name, server)
    
    tools = await get_server_tools(server)
    
    return ServerResponse(
        name=name,
        type=server.type,
        url=server.url,
        headers=server.headers,
        requestTransform=server.requestTransform,
        responseTransform=server.responseTransform,
        toolsCount=len(tools)
    )


@router.delete("/admin/servers/{name}")
async def delete_server(name: str) -> Dict[str, str]:
    success = ConfigLoader.remove_server(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found")
    
    return {"message": f"Server '{name}' deleted successfully"}


@router.post("/admin/reload")
async def reload_config() -> Dict[str, str]:
    ConfigLoader.reload()
    return {"message": "Configuration reloaded successfully"}
