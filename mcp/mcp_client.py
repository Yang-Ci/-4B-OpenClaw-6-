#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client - HTTP 传输协议客户端
功能：连接 MCP Server 并调用其中的工具
"""

import sys
import io

# 修复 Windows 终端编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import httpx
import asyncio
from typing import Any, Dict, Optional


class MCPClient:
    """MCP HTTP 客户端"""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8080"):
        """
        初始化 MCP 客户端
        
        Args:
            server_url: MCP 服务器地址
        """
        self.server_url = server_url
        self.base_url = f"{server_url}/mcp"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.session_id: Optional[str] = None
        
    async def connect(self) -> bool:
        """
        连接到 MCP 服务器
        
        Returns:
            连接是否成功
        """
        try:
            # 发送初始化请求
            response = await self.client.post(
                f"{self.base_url}/message",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "MCP Client",
                            "version": "1.0.0"
                        }
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 已连接到 MCP 服务器")
                print(f"   服务器：{data.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
                print(f"   版本：{data.get('result', {}).get('serverInfo', {}).get('version', 'Unknown')}")
                return True
            else:
                print(f"❌ 连接失败：{response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 连接错误：{e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用 MCP 工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/message",
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('result', {})
                
                # 提取结果内容
                if 'content' in result and len(result['content']) > 0:
                    content = result['content'][0]
                    if content.get('type') == 'text':
                        return content.get('text')
                    return content
                return result
            else:
                raise Exception(f"调用失败：{response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 工具调用错误：{e}")
            raise
    
    async def list_tools(self) -> list:
        """
        列出所有可用工具
        
        Returns:
            工具列表
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/message",
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/list",
                    "params": {}
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get('result', {}).get('tools', [])
                return tools
            else:
                print(f"❌ 获取工具列表失败：{response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 错误：{e}")
            return []
    
    async def get_resource(self, uri: str) -> str:
        """
        获取资源内容
        
        Args:
            uri: 资源 URI
            
        Returns:
            资源内容
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/message",
                json={
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "resources/read",
                    "params": {
                        "uri": uri
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                contents = data.get('result', {}).get('contents', [])
                if contents and len(contents) > 0:
                    return contents[0].get('text', '')
                return ''
            else:
                print(f"❌ 获取资源失败：{response.status_code}")
                return ''
                
        except Exception as e:
            print(f"❌ 错误：{e}")
            return ''
    
    async def disconnect(self):
        """断开连接"""
        await self.client.aclose()
        print("👋 已断开连接")


# ==================== 便捷函数 ====================

async def test_all_tools():
    """测试所有工具"""
    client = MCPClient("http://127.0.0.1:8080")
    
    # 连接服务器
    if not await client.connect():
        return
    
    print("\n" + "=" * 60)
    print("获取工具列表...")
    print("=" * 60)
    
    tools = await client.list_tools()
    for tool in tools:
        print(f"\n🔧 工具：{tool.get('name')}")
        print(f"   描述：{tool.get('description', '无')}")
    
    print("\n" + "=" * 60)
    print("测试工具调用...")
    print("=" * 60)
    
    # 测试加法
    print("\n➕ 测试加法 (5 + 3):")
    result = await client.call_tool("add", {"a": 5, "b": 3})
    print(f"   结果：{result}")
    
    # 测试乘法
    print("\n✖️ 测试乘法 (4 × 7):")
    result = await client.call_tool("multiply", {"a": 4, "b": 7})
    print(f"   结果：{result}")
    
    # 测试减法
    print("\n➖ 测试减法 (10 - 3):")
    result = await client.call_tool("subtract", {"a": 10, "b": 3})
    print(f"   结果：{result}")
    
    # 测试除法
    print("\n➗ 测试除法 (20 ÷ 4):")
    result = await client.call_tool("divide", {"a": 20, "b": 4})
    print(f"   结果：{result}")
    
    # 测试获取资源
    print("\n" + "=" * 60)
    print("测试资源访问...")
    print("=" * 60)
    
    print("\n📚 获取服务器名称:")
    name = await client.get_resource("info://server/name")
    print(f"   {name}")
    
    print("\n📚 获取服务器版本:")
    version = await client.get_resource("info://server/version")
    print(f"   {version}")
    
    print("\n📚 获取工具列表:")
    tools_info = await client.get_resource("info://server/tools")
    print(f"   {tools_info}")
    
    # 断开连接
    await client.disconnect()


def run_sync_test():
    """同步运行测试"""
    asyncio.run(test_all_tools())


# ==================== 主函数 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Client - HTTP 传输协议")
    print("=" * 60)
    print("开始测试 MCP 服务器连接...")
    print("=" * 60)
    
    # 运行测试
    run_sync_test()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
