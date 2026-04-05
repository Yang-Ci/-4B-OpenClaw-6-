# MCP 文件夹说明

本文件夹包含 MCP (Model Context Protocol) 相关的服务器和客户端代码。

## 📁 文件结构

### 核心文件

1. **服务器文件**
   - `mcp_server_http.py` - MCP Server (HTTP 传输协议)
   - `mcp_server_web.py` - MCP Server (带 Web 配置界面)
   - `mcp_server.py` - MCP Server (基础版本)

2. **客户端文件**
   - `mcp_client_sync.py` - MCP Client (同步版本，推荐使用)
   - `mcp_client.py` - MCP Client (异步版本)

3. **配置文件**
   - `mcp_config.json` - MCP 配置文件
   - `mcp_config_ui.html` - Web 版配置界面

4. **文档文件**
   - `MCP_CLIENT_GUIDE.md` - Client 使用指南
   - `MCP_HTTP_GUIDE.md` - HTTP 模式配置指南
   - `MCP_SETUP_GUIDE.md` - 安装配置指南
   - `README_MCP_HTTP.md` - HTTP 模式快速入门

5. **测试文件**
   - `test_mcp_server.py` - 服务器测试脚本

## 🚀 快速开始

### 1. 启动 MCP Server

```bash
# 从 audio 目录运行
conda activate voice_assistant_env
python mcp/mcp_server_simple.py
```

服务器会运行在 `http://127.0.0.1:8081/mcp`

### 2. 在代码中使用 Client

```python
import sys
sys.path.insert(0, 'mcp')  # 添加 mcp 目录到路径

from mcp_client_sync import MCPClient

# 创建客户端
client = MCPClient("http://127.0.0.1:8081")

# 连接并调用工具
if client.connect():
    # 调用工具
    result = client.call_tool("add", {"a": 5, "b": 3})
    print(f"5 + 3 = {result}")
    
    # 断开连接
    client.disconnect()
```

## 📦 可用工具

所有 MCP Server 都提供以下工具:

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `add` | 加法 | `a: int`, `b: int` |
| `multiply` | 乘法 | `a: int`, `b: int` |
| `subtract` | 减法 | `a: int`, `b: int` |
| `divide` | 除法 | `a: float`, `b: float` |

## 🔧 环境要求

- Python 3.10+
- fastmcp
- httpx
- flask (仅 Web 版本需要)

## 📝 注意事项

1. **端口配置**: 默认使用 8081 端口，如有冲突请修改服务器代码中的端口设置
2. **Session 管理**: 客户端会自动管理 session ID，无需手动处理
3. **编码问题**: Windows 终端已自动处理 UTF-8 编码

---

**更新日期**: 2026-03-26
