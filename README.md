## MCP Gateway (Dockerized)

A lightweight Python FastAPI application that converts any MCP provider to standard protocols: streamable-http, SSE, and stdio. It supports token-based auth, provides JSON templates, a responsive UI for management, and Docker deployment.

### 需求分析摘要
- **协议转换**: 
  - 若输入本身为三种标准协议之一，走模板/直通转换。
  - 若为自定义协议，支持提供自定义脚本 `transform(spec, target)` 完成映射。
- **鉴权**: Bearer Token（可选）。若未配置 `MCP_GATEWAY_TOKEN`，API默认开放。
- **产出**: 生成三种协议的 JSON 文件模板，便于其他客户端直接调用。
- **UI**: 响应式、轻量、美观的管理界面，查看模板、做转换、查看工具信息。
- **MCP管理**: 注册表、心跳检测（占位）、工具数量与详情（占位接口）。
- **Docker**: 多阶段构建，镜像小、资源占用低。

### 目录结构
```
backend/
  app/
    api/
      v1/
        adapters.py
        converter.py
        mcp.py
      routes.py
    adapters/
      __init__.py
      base.py
      standard.py
      custom.py
    core/
      auth.py
      config.py
    schemas/
      protocols.py
    services/
      converter.py
      registry.py
    __init__.py
    main.py
configs/
  streamable-http.json
  sse.json
  stdio.json
ui/
  index.html
  styles.css
  main.js
.cursorrules
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

### 运行
- 本地（Python 3.12+）：
```bash
pip install -r requirements.txt
# 可选：复制并编辑环境变量
cp .env.example .env  # 视操作系统而定
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```
- Docker：
```bash
docker build -t mcp-gateway .
docker run -p 8000:8000 --env-file .env mcp-gateway
# 或 docker compose
docker compose up --build -d
```

访问：`http://localhost:8000/ui`

### 环境变量
- `MCP_GATEWAY_TOKEN`: Bearer Token（可选）。存在时接口需鉴权。
- `MCP_GATEWAY_SECRET`: 应用密钥（占位），默认开发值。
- `CORS_ALLOW_ORIGINS`: 逗号分隔白名单，默认 `*`。
- `MCP_CONFIG_DIR`: 模板目录，默认 `configs`。
- `UI_PATH`: UI 目录，默认 `ui`。

### API 概览
- 健康检查: `GET /health`
- 模板列表: `GET /api/v1/adapters/templates`
- 协议转换: `POST /api/v1/converter/convert`
  - 请求体：
```json
{
  "source": {"name": "custom", "endpoint": "http://...", "auth_token": "...", "config": {}},
  "target": "streamable-http|sse|stdio",
  "custom_script": "optional Python code defining transform(spec, target)"
}
```
  - 响应：`{"result": { ... }}`
- MCP 注册表（占位）:
  - `GET /api/v1/mcp/registry`
  - `GET /api/v1/mcp/heartbeat`
  - `GET /api/v1/mcp/tools`
  - `GET /api/v1/mcp/tools/{tool_id}`

### 自定义协议转换脚本
- `custom_script` 中需提供函数：
```python
def transform(spec, target):
    # spec: dict 输入协议描述
    # target: "streamable-http" | "sse" | "stdio"
    return {"protocol": target, **spec}
```
注意：当前示例以 `exec` 执行，生产环境应使用沙箱隔离（如 subprocess + 容器/wasm sandbox）。

### JSON 模板
- `configs/streamable-http.json`
- `configs/sse.json`
- `configs/stdio.json`

### UI
- 地址：`/ui`
- 功能：
  - 查看并下载模板
  - 进行协议转换并展示结果
  - 查看 MCP 工具（占位数据）

### 安全与鉴权
- 若设置 `MCP_GATEWAY_TOKEN`，所有受保护的 API 需请求头 `Authorization: Bearer <token>`。
- 未设置时，系统默认开放（便于开发测试）。

### 备注
- 参考 MCP Python SDK 可进一步实现真实数据通道与工具发现：`modelcontextprotocol/python-sdk`。
- 现有 MCP 心跳/工具接口为占位，后续可接入真实 MCP 提供方并做轮询/推送检测。
