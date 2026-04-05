#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server - HTTP 传输协议版本
功能：实现 MCP 协议的 HTTP 服务端，支持浏览器访问和配置
"""

from fastmcp import FastMCP

# 创建 MCP 实例，配置 HTTP 传输协议
mcp = FastMCP(
    "MCP Server HTTP",
    host="127.0.0.1",
    port=8080
)


# ==================== 工具定义 ====================

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
    result = a + b
    print(f"计算：{a} + {b} = {result}")
    return result


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    两个数相乘
    
    Args:
        a: 第一个整数
        b: 第二个整数
    
    Returns:
        两个整数的积
    """
    result = a * b
    print(f"计算：{a} × {b} = {result}")
    return result


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """
    两个数相减
    
    Args:
        a: 被减数
        b: 减数
    
    Returns:
        两个整数的差
    """
    result = a - b
    print(f"计算：{a} - {b} = {result}")
    return result


@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    两个数相除
    
    Args:
        a: 被除数
        b: 除数
    
    Returns:
        两个数的商
    """
    if b == 0:
        raise ValueError("除数不能为 0")
    result = a / b
    print(f"计算：{a} ÷ {b} = {result}")
    return result


# ==================== 资源定义 ====================

@mcp.resource("info://server/name")
def get_server_name() -> str:
    """获取服务器名称"""
    return "MCP Server HTTP"


@mcp.resource("info://server/version")
def get_server_version() -> str:
    """获取服务器版本"""
    return "1.0.0"


@mcp.resource("info://server/tools")
def list_tools() -> str:
    """列出所有可用工具"""
    tools = [
        "add - 两个数相加",
        "multiply - 两个数相乘",
        "subtract - 两个数相减",
        "divide - 两个数相除"
    ]
    return "\n".join(tools)


# ==================== Prompt 定义 ====================

@mcp.prompt()
def calculator_prompt(operation: str, a: int, b: int) -> str:
    """
    生成计算器提示词
    
    Args:
        operation: 操作类型 (add, subtract, multiply, divide)
        a: 第一个数
        b: 第二个数
    
    Returns:
        提示词字符串
    """
    return f"请执行{operation}操作：{a} 和 {b}"


# ==================== 主函数 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Server - HTTP 模式")
    print("=" * 60)
    print("服务器地址：http://127.0.0.1:8080")
    print("SSE 端点：http://127.0.0.1:8080/sse")
    print("HTTP POST 端点：http://127.0.0.1:8080/message")
    print("=" * 60)
    print("启动服务器...")
    print("=" * 60)
    
    # 启动 MCP Server，使用 HTTP 传输协议
    mcp.run(transport="streamable-http")
