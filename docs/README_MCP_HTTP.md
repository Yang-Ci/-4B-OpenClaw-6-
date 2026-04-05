# 🌐 MCP HTTP 浏览器配置 - 快速指南

## ✅ 已完成配置

MCP Server 现在支持 **HTTP 传输协议**,可以通过浏览器进行操作和配置!

## 🚀 启动方式

### 方式 1: Web 控制台模式 (推荐)

```bash
conda activate voice_assistant_env
python mcp_server_web.py
```

**访问地址:**
- 🌐 Web 控制台：`http://127.0.0.1:5000` (自动打开)
- 🔌 MCP 服务器：`http://127.0.0.1:8000/mcp`

### 方式 2: 纯 HTTP 模式

```bash
conda activate voice_assistant_env
python mcp_server_http.py
```

**访问地址:**
- 🔌 MCP 服务器：`http://127.0.0.1:8080`

## 🎯 浏览器功能

### Web 控制台 (`http://127.0.0.1:5000`)

1. **实时监控** - 查看服务器运行状态
2. **工具测试** - 直接在浏览器中测试 MCP 工具
   - ➕ add (加法)
   - ✖️ multiply (乘法)
   - ➖ subtract (减法)
   - ➗ divide (除法)
3. **API 端点查看** - 显示所有可用的端点

### 测试示例

在浏览器中输入数字，点击"测试"按钮:
- 测试加法：输入 5 和 3 → 结果显示 8
- 测试乘法：输入 4 和 7 → 结果显示 28
- 测试减法：输入 10 和 3 → 结果显示 7
- 测试除法：输入 20 和 4 → 结果显示 5.0

## 📡 API 端点

### MCP HTTP 端点

- **SSE 端点**: `http://127.0.0.1:8000/mcp/sse`
- **POST 端点**: `http://127.0.0.1:8000/mcp/message`

### 使用 curl 测试

```bash
# 测试加法
curl -X POST http://127.0.0.1:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{"method": "add", "params": {"a": 5, "b": 3}}'

# 测试乘法
curl -X POST http://127.0.0.1:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{"method": "multiply", "params": {"a": 4, "b": 7}}'
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `mcp_server_web.py` | 带 Web 界面的 MCP 服务器 |
| `mcp_server_http.py` | 纯 HTTP 模式的 MCP 服务器 |
| `mcp_config_ui.html` | 独立的配置界面 (静态 HTML) |
| `MCP_HTTP_GUIDE.md` | 详细的 HTTP 配置指南 |

## ⚙️ 配置选项

### 修改端口

编辑 `mcp_server_web.py`:

```python
os.environ['FASTMCP_PORT'] = '8080'  # 修改 MCP 端口
app.run(host='127.0.0.1', port=5000)  # 修改 Web 端口
```

### 允许外部访问

```python
os.environ['FASTMCP_HOST'] = '0.0.0.0'  # 允许所有 IP
app.run(host='0.0.0.0', port=5000)
```

## 🔧 常用命令

```bash
# 激活环境
conda activate voice_assistant_env

# 启动 Web 控制台
python mcp_server_web.py

# 启动纯 HTTP 模式
python mcp_server_http.py

# 测试服务器
curl http://127.0.0.1:8000/mcp
```

## 💡 优势

✅ **可视化操作** - 无需命令行，浏览器即可操作  
✅ **实时测试** - 即时查看工具运行结果  
✅ **配置管理** - 轻松修改服务器配置  
✅ **跨平台** - 任何有浏览器的设备都能访问  
✅ **易于集成** - 标准 HTTP 协议，易于与其他系统集成

## 📖 详细文档

查看 [`MCP_HTTP_GUIDE.md`](MCP_HTTP_GUIDE.md) 获取完整的使用指南和高级功能。

---

**现在您可以在浏览器中操作和配置 MCP Server 了!** 🎉
