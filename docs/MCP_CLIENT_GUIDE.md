# MCP Client 使用指南

## 📋 概述

MCP Client 用于连接 MCP Server 并调用其中提供的工具。

## 🚀 快速开始

### 1. 启动 MCP Server

首先启动 HTTP 模式的 MCP 服务器:

```bash
conda activate voice_assistant_env
python mcp_server_http.py
```

或者启动带 Web 界面的版本:

```bash
conda activate voice_assistant_env
python mcp_server_web.py
```

### 2. 运行客户端

**同步版本 (推荐):**

```bash
python mcp_client_sync.py
```

**异步版本:**

```bash
python mcp_client.py
```

## 📖 使用方法

### 方式一：完整测试

运行内置测试:

```bash
python mcp_client_sync.py
```

输出示例:

```
============================================================
MCP Client - HTTP 传输协议
============================================================
开始测试 MCP 服务器连接...
============================================================
✅ 已连接到 MCP 服务器
   服务器：MCP Server HTTP
   版本：1.0.0

============================================================
获取工具列表...
============================================================

🔧 工具：add
   描述：两个数相加

🔧 工具：multiply
   描述：两个数相乘

🔧 工具：subtract
   描述：两个数相减

🔧 工具：divide
   描述：两个数相除

============================================================
测试工具调用...
============================================================

➕ 测试加法 (5 + 3):
   结果：8

✖️ 测试乘法 (4 × 7):
   结果：28

➖ 测试减法 (10 - 3):
   结果：7

➗ 测试除法 (20 ÷ 4):
   结果：5.0

============================================================
测试资源访问...
============================================================

📚 获取服务器名称:
   MCP Server HTTP

📚 获取服务器版本:
   1.0.0

📚 获取工具列表:
   add - 两个数相加
   multiply - 两个数相乘
   subtract - 两个数相减
   divide - 两个数相除

👋 已断开连接
```

### 方式二：在自己的代码中使用

#### 同步版本示例

```python
from mcp_client_sync import MCPClient

# 创建客户端
client = MCPClient("http://127.0.0.1:8080")

# 连接服务器
if client.connect():
    # 调用工具
    result = client.call_tool("add", {"a": 10, "b": 20})
    print(f"结果：{result}")  # 输出：30
    
    # 获取工具列表
    tools = client.list_tools()
    for tool in tools:
        print(f"工具：{tool['name']}")
    
    # 断开连接
    client.disconnect()
```

#### 使用上下文管理器 (推荐)

```python
from mcp_client_sync import MCPClient

# 自动连接和断开
with MCPClient("http://127.0.0.1:8080") as client:
    result = client.call_tool("multiply", {"a": 6, "b": 7})
    print(f"6 × 7 = {result}")  # 输出：42
```

#### 异步版本示例

```python
import asyncio
from mcp_client import MCPClient

async def main():
    client = MCPClient("http://127.0.0.1:8080")
    
    # 连接服务器
    if await client.connect():
        # 调用工具
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"结果：{result}")
        
        # 断开连接
        await client.disconnect()

# 运行异步代码
asyncio.run(main())
```

## 🔧 API 参考

### MCPClient 类

#### 初始化

```python
client = MCPClient(server_url="http://127.0.0.1:8080")
```

**参数:**
- `server_url`: MCP 服务器地址 (默认：http://127.0.0.1:8080)

#### connect()

连接到 MCP 服务器

```python
if client.connect():
    print("连接成功!")
```

**返回:** `bool` - 连接是否成功

#### call_tool(tool_name, arguments)

调用指定的工具

```python
result = client.call_tool("add", {"a": 10, "b": 20})
print(result)  # 输出：30
```

**参数:**
- `tool_name`: 工具名称 (如 "add", "multiply")
- `arguments`: 工具参数字典

**返回:** 工具执行结果

#### list_tools()

获取所有可用工具

```python
tools = client.list_tools()
for tool in tools:
    print(f"工具：{tool['name']}")
    print(f"描述：{tool.get('description', '无')}")
```

**返回:** 工具列表 (List[Dict])

#### get_resource(uri)

获取指定资源的内容

```python
name = client.get_resource("info://server/name")
print(f"服务器名称：{name}")
```

**参数:**
- `uri`: 资源 URI (如 "info://server/name")

**返回:** 资源内容 (字符串)

#### disconnect()

断开与服务器的连接

```python
client.disconnect()
```

## 📚 可用工具

### 1. add - 加法

两个整数相加

```python
result = client.call_tool("add", {"a": 5, "b": 3})
# 返回：8
```

### 2. multiply - 乘法

两个整数相乘

```python
result = client.call_tool("multiply", {"a": 4, "b": 7})
# 返回：28
```

### 3. subtract - 减法

两个数相减

```python
result = client.call_tool("subtract", {"a": 10, "b": 3})
# 返回：7
```

### 4. divide - 除法

两个数相除

```python
result = client.call_tool("divide", {"a": 20, "b": 4})
# 返回：5.0
```

## 📚 可用资源

### info://server/name

获取服务器名称

```python
name = client.get_resource("info://server/name")
# 返回："MCP Server HTTP"
```

### info://server/version

获取服务器版本

```python
version = client.get_resource("info://server/version")
# 返回："1.0.0"
```

### info://server/tools

获取工具列表

```python
tools = client.get_resource("info://server/tools")
# 返回：工具列表文本
```

## ⚠️ 错误处理

```python
from mcp_client_sync import MCPClient

client = MCPClient("http://127.0.0.1:8080")

try:
    if client.connect():
        result = client.call_tool("add", {"a": 5, "b": 3})
        print(f"结果：{result}")
except Exception as e:
    print(f"发生错误：{e}")
finally:
    client.disconnect()
```

## 🔍 调试技巧

### 1. 检查服务器是否运行

```bash
curl http://127.0.0.1:8080/mcp
```

### 2. 测试连接

```python
client = MCPClient()
if client.connect():
    print("✅ 服务器可访问")
else:
    print("❌ 服务器不可访问")
```

### 3. 查看详细错误

```python
try:
    result = client.call_tool("add", {"a": 5, "b": 3})
except Exception as e:
    print(f"错误类型：{type(e).__name__}")
    print(f"错误信息：{str(e)}")
```

## 💡 最佳实践

1. **使用上下文管理器** - 自动管理连接和断开
2. **检查连接状态** - 在调用工具前确保连接成功
3. **异常处理** - 捕获并处理可能的错误
4. **资源释放** - 使用完及时断开连接

## 📝 完整示例

```python
from mcp_client_sync import MCPClient

def calculator_demo():
    """计算器演示"""
    with MCPClient("http://127.0.0.1:8080") as client:
        print("=== 计算器演示 ===\n")
        
        # 加法
        a, b = 15, 27
        result = client.call_tool("add", {"a": a, "b": b})
        print(f"{a} + {b} = {result}")
        
        # 乘法
        a, b = 12, 8
        result = client.call_tool("multiply", {"a": a, "b": b})
        print(f"{a} × {b} = {result}")
        
        # 减法
        a, b = 100, 37
        result = client.call_tool("subtract", {"a": a, "b": b})
        print(f"{a} - {b} = {result}")
        
        # 除法
        a, b = 144, 12
        result = client.call_tool("divide", {"a": a, "b": b})
        print(f"{a} ÷ {b} = {result}")

if __name__ == "__main__":
    calculator_demo()
```

---

**祝您使用愉快!** 🎉
