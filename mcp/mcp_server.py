#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server 示例
功能：实现 MCP 协议的服务端，提供 add 工具
"""

from fastmcp import FastMCP

# 创建 MCP 实例
mcp = FastMCP("MCP Server Demo")


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


# ==================== 资源定义（可选） ====================

@mcp.resource("info://server/name")
def get_server_name() -> str:
    """获取服务器名称"""
    return "MCP Server Demo"


@mcp.resource("info://server/version")
def get_server_version() -> str:
    """获取服务器版本"""
    return "1.0.0"


# ==================== Prompt 定义（可选） ====================

@mcp.prompt()
def calculator_prompt(operation: str, a: int, b: int) -> str:
    """
    生成计算器提示词
    
    Args:
        operation: 操作类型 (add, subtract, multiply)
        a: 第一个数
        b: 第二个数
    
    Returns:
        提示词字符串
    """
    return f"请执行{operation}操作：{a} 和 {b}"


# ==================== 主函数 ====================

if __name__ == "__main__":
    # 启动 MCP Server
    # 默认使用 stdio 传输方式
    mcp.run()
