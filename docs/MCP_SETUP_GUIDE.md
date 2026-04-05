# MCP Server 实现流程

## 1. 安装 FastMCP

```bash
pip install fastmcp
```

## 2. 创建 MCP Server 步骤

### 步骤 1: 导入 FastMCP
```python
from fastmcp import FastMCP
```

### 步骤 2: 创建 MCP 实例
```python
mcp = FastMCP("MCP Server Demo")
```

### 步骤 3: 定义工具（Tool）
使用 `@mcp.tool()` 装饰器定义工具：

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    两个数相加
    
    Args:
        a: 第一个整数
        b: 第二个整数
    
    Returns:
        两个整数的和
    """
    return a + b
```

### 步骤 4: （可选）定义资源（Resource）
```python
@mcp.resource("info://server/name")
def get_server_name() -> str:
    """获取服务器名称"""
    return "MCP Server Demo"
```

### 步骤 5: （可选）定义 Prompt
```python
@mcp.prompt()
def calculator_prompt(operation: str, a: int, b: int) -> str:
    """生成计算器提示词"""
    return f"请执行{operation}操作：{a} 和 {b}"
```

### 步骤 6: 启动 Server
```python
if __name__ == "__main__":
    mcp.run()
```

## 3. 文件说明

| 文件 | 说明 |
|------|------|
| `mcp_server.py` | MCP Server 主文件 |
| `mcp_config.json` | MCP 配置文件（用于客户端连接） |
| `test_mcp_server.py` | 测试脚本 |

## 4. 运行方式

### 方式 1: 直接运行 Server
```bash
python mcp_server.py
```

### 方式 2: 使用配置文件
在支持 MCP 的客户端中配置 `mcp_config.json`

### 方式 3: 测试脚本
```bash
python test_mcp_server.py
```

## 5. MCP 核心概念

### Tool（工具）
- 可被调用的函数
- 有明确的输入参数和返回值
- 使用 `@mcp.tool()` 装饰器定义

### Resource（资源）
- 提供数据的只读端点
- 使用 URI 标识
- 使用 `@mcp.resource()` 装饰器定义

### Prompt（提示词）
- 生成用于与大模型交互的提示词
- 使用 `@mcp.prompt()` 装饰器定义

## 6. 传输方式

FastMCP 支持多种传输方式：

### Stdio（默认）
```python
mcp.run()  # 使用 stdin/stdout
```

### HTTP
```python
mcp.run(transport="http")
```

### WebSocket
```python
mcp.run(transport="sse")
```

## 7. 完整示例

```python
from fastmcp import FastMCP

# 创建 MCP 实例
mcp = FastMCP("My Server")

# 定义工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """两个数相加"""
    return a + b

# 定义资源
@mcp.resource("info://version")
def version() -> str:
    return "1.0.0"

# 定义 prompt
@mcp.prompt()
def greet(name: str) -> str:
    return f"请向 {name} 问好"

# 启动 server
if __name__ == "__main__":
    mcp.run()
```

## 8. 调试技巧

1. **打印日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **测试工具函数**
   ```python
   from mcp_server import add
   result = add(1, 2)
   print(result)
   ```

3. **查看注册的工具**
   ```python
   from mcp_server import mcp
   print(mcp._tools)
   ```

## 9. 常见问题

### Q: 如何添加更多工具？
A: 只需添加新的 `@mcp.tool()` 装饰器函数即可

### Q: 如何修改工具参数？
A: 修改函数的参数类型和文档字符串

### Q: 如何部署到生产环境？
A: 使用 HTTP 或 WebSocket 传输方式，并配置适当的服务器

## 10. 参考资源

- [FastMCP 官方文档](https://github.com/jlowin/fastmcp)
- [MCP 协议规范](https://modelcontextprotocol.io/)
