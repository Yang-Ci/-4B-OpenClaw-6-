# MCP Server HTTP 配置指南

## 📋 概述

MCP (Model Context Protocol) 支持 HTTP 传输协议，允许您通过浏览器进行操作和配置。

## 🚀 快速开始

### 方式一：纯 HTTP 模式

运行 MCP Server（HTTP 传输协议）:

```bash
conda activate voice_assistant_env
python mcp_server_http.py
```

**访问地址:**
- MCP 服务器：`http://127.0.0.1:8080`
- SSE 端点：`http://127.0.0.1:8080/sse`
- POST 端点：`http://127.0.0.1:8080/message`

### 方式二：Web 控制台模式（推荐）

运行带 Web 界面的 MCP Server:

```bash
conda activate voice_assistant_env
python mcp_server_web.py
```

**访问地址:**
- Web 控制台：`http://127.0.0.1:5000` (自动在浏览器中打开)
- MCP 服务器：`http://127.0.0.1:8080`

## 🌐 浏览器配置界面

### 功能特性

1. **实时监控** - 查看服务器状态和连接信息
2. **工具测试** - 在浏览器中直接测试 MCP 工具
3. **配置管理** - 修改服务器配置（主机、端口、传输协议）
4. **API 文档** - 查看所有可用的端点和资源

### 界面说明

打开浏览器访问 `http://127.0.0.1:5000` 后，您将看到:

- **服务器状态栏** - 显示当前运行状态
- **工具测试区域** - 提供交互式测试界面
- **API 端点列表** - 所有可用的 HTTP 端点
- **配置表单** - 修改服务器参数

## 🛠️ 可用工具

### 1. add - 加法
```json
{
  "method": "add",
  "params": {"a": 5, "b": 3}
}
```

### 2. multiply - 乘法
```json
{
  "method": "multiply",
  "params": {"a": 4, "b": 7}
}
```

### 3. subtract - 减法
```json
{
  "method": "subtract",
  "params": {"a": 10, "b": 3}
}
```

### 4. divide - 除法
```json
{
  "method": "divide",
  "params": {"a": 20, "b": 4}
}
```

## 📡 测试方法

### 使用 curl 测试

```bash
# 测试加法
curl -X POST http://127.0.0.1:8080/message \
  -H "Content-Type: application/json" \
  -d '{"method": "add", "params": {"a": 5, "b": 3}}'

# 测试乘法
curl -X POST http://127.0.0.1:8080/message \
  -H "Content-Type: application/json" \
  -d '{"method": "multiply", "params": {"a": 4, "b": 7}}'
```

### 使用浏览器控制台测试

1. 打开 `http://127.0.0.1:5000`
2. 在工具测试区域输入参数
3. 点击"测试"按钮
4. 查看实时结果

## ⚙️ 配置选项

### 修改服务器配置

在 Web 控制台中:

1. 修改 **主机地址** (默认：127.0.0.1)
2. 修改 **端口号** (默认：8080)
3. 选择 **传输协议**:
   - Streamable HTTP (推荐)
   - Standard IO
   - Server-Sent Events
4. 点击 **保存配置**
5. 点击 **重启服务器** 应用新配置

### 配置文件

配置会保存在 `mcp_config.json`:

```json
{
  "host": "127.0.0.1",
  "port": 8080,
  "transport": "streamable-http"
}
```

## 🔗 连接到 MCP 客户端

### JavaScript 示例

```javascript
const mcpClient = new MCPClient({
  transport: 'streamable-http',
  url: 'http://127.0.0.1:8080'
});

// 调用工具
const result = await mcpClient.callTool('add', {a: 5, b: 3});
console.log(result); // 输出：8
```

### Python 示例

```python
from mcp import Client

client = Client(
    transport='streamable-http',
    url='http://127.0.0.1:8080'
)

# 调用工具
result = client.call_tool('add', {'a': 5, 'b': 3})
print(result)  # 输出：8
```

## 📚 可用资源

### 服务器信息资源

- `info://server/name` - 获取服务器名称
- `info://server/version` - 获取服务器版本
- `info://server/tools` - 列出所有可用工具

### 访问资源

```bash
curl http://127.0.0.1:8080/resource/info://server/name
```

## 🎯 高级功能

### 自定义工具

在 `mcp_server_web.py` 中添加新的工具:

```python
@mcp.tool()
def custom_tool(param1: str, param2: int) -> str:
    """自定义工具描述"""
    # 实现逻辑
    return result
```

### 自定义资源

```python
@mcp.resource("custom://data/info")
def get_custom_info() -> str:
    """获取自定义信息"""
    return "Custom information here"
```

### 自定义 Prompt

```python
@mcp.prompt()
def custom_prompt(topic: str) -> str:
    """生成自定义提示词"""
    return f"Please help me with {topic}"
```

## 🔒 安全配置

### 限制访问 IP

修改主机地址为 `0.0.0.0` 允许外部访问:

```python
mcp = FastMCP(
    "MCP Server",
    host="0.0.0.0",  # 允许所有 IP 访问
    port=8080
)
```

### 添加认证

在生产环境中，建议添加认证机制:

```python
from flask import request, abort

@app.before_request
def check_auth():
    api_key = request.headers.get('X-API-Key')
    if api_key != 'your-secret-key':
        abort(401)
```

## 📖 参考链接

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://github.com/modelcontextprotocol/fastmcp)
- [HTTP 传输协议规范](https://modelcontextprotocol.io/docs/concepts/transports#http)

## 💡 常见问题

### Q: 浏览器无法访问服务器？
A: 检查防火墙设置，确保端口 8080 和 5000 未被阻止。

### Q: 如何更改默认端口？
A: 在 Web 控制台中修改配置，或直接修改代码中的端口参数。

### Q: 支持 HTTPS 吗？
A: 支持。需要配置 SSL 证书，建议使用反向代理（如 Nginx）处理 HTTPS。

### Q: 可以同时连接多个客户端吗？
A: 是的，MCP Server 支持多个客户端同时连接。

---

**祝您使用愉快！** 🎉
