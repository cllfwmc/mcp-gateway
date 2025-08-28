# MCP Gateway

一个将只支持 streamable-http 的 MCP Server 扩展为三种协议入口的中间层：
- POST `/mcp`：直通转发（支持请求/响应转换）
- GET `/sse`：将上游流转为 Server-Sent Events（请求支持 `q` 传 JSON）
- 本地 `stdio`：`python -m gateway.app.stdio_bridge`

## 运行
### 本地
```bash
pip install -r requirements.txt
uvicorn gateway.app.main:app --host 0.0.0.0 --port 8000
```
访问 `http://localhost:8000` 使用内置 UI。

### Docker
```bash
docker compose up --build
```

## 配置 `config.yaml`
```yaml
mcpServers:
  ezbookkeeping-mcp:
    type: streamable-http
    url: http://127.0.0.1:1234/mcp
    headers:
      Authorization: Bearer ${TOKEN}
    requestTransform: default
    responseTransform: default
```
- 支持 `${ENV}` 环境变量插值（仅 headers）。
- 可配置不同服务名，通过 `?server=` 指定。

## 转换器（transforms）
- 内置注册表，名称到 `transform(payload: dict) -> dict` 的映射。
- 自定义脚本放到 `transforms/custom/*.py`，文件名即名称。
- 示例：`transforms/custom/example_uppercase.py`。

## stdio 桥
```bash
python -m gateway.app.stdio_bridge
```
- 从标准输入逐行读取 JSON，调用默认或 `__server__` 指定的服务：
```bash
echo '{"__server__":"ezbookkeeping-mcp","jsonrpc":"2.0","id":"1","method":"ping"}' | python -m gateway.app.stdio_bridge
```
- 输出逐行（NDJSON），响应同样应用 `responseTransform`。

## UI
- Jinja2 + Tailwind CDN，无需构建。
- 首页展示服务清单与快速测试（`/mcp` 与 `/sse`）。
