#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client - 同步版本
功能：连接 MCP Server 并调用其中的工具（同步 API）
"""

import sys
import io
import json
import re

# 修复 Windows 终端编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import httpx
from typing import Any, Dict, List, Optional


class MCPClient:
    """MCP HTTP 同步客户端"""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8080"):
        """
        初始化 MCP 客户端
        
        Args:
            server_url: MCP 服务器地址 (不要带 /mcp 后缀)
        """
        self.server_url = server_url.rstrip('/')  # 移除末尾斜杠
        self.base_url = f"{self.server_url}/mcp"  # MCP 端点
        self.client = httpx.Client(timeout=30.0)
        self.headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        self.session_id: Optional[str] = None
        
    def connect(self) -> bool:
        """连接到 MCP 服务器"""
        try:
            response = self.client.post(
                self.base_url,
                headers=self.headers,
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
                # 从响应头获取 session ID (MCP 协议使用 Mcp-Session-Id header)
                self.session_id = response.headers.get('Mcp-Session-Id')
                
                # 提取 SSE 事件中的数据
                content = response.text
                # 解析 SSE 格式：查找 data: 开头的行
                data = None
                for line in content.split('\n'):
                    if line.startswith('data:'):
                        try:
                            data = json.loads(line[5:].strip())
                            break
                        except:
                            continue
                
                if data is None:
                    try:
                        data = response.json()
                    except:
                        print(f"❌ 无法解析响应：{content[:200]}")
                        return False
                
                print(f"✅ 已连接到 MCP 服务器")
                print(f"   服务器：{data.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
                print(f"   版本：{data.get('result', {}).get('serverInfo', {}).get('version', 'Unknown')}")
                if self.session_id:
                    print(f"   Session ID: {self.session_id}")
                
                return True
            else:
                print(f"❌ 连接失败：{response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 连接错误：{e}")
            return False
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用 MCP 工具"""
        try:
            headers = self.headers.copy()
            if self.session_id:
                headers["Mcp-Session-Id"] = self.session_id
            
            response = self.client.post(
                self.base_url,
                headers=headers,
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
                # 提取 SSE 事件中的数据
                content = response.text
                # 解析 SSE 格式：查找 data: 开头的行
                data = None
                for line in content.split('\n'):
                    if line.startswith('data:'):
                        try:
                            data = json.loads(line[5:].strip())
                            break
                        except:
                            continue
                
                if data is None:
                    try:
                        data = response.json()
                    except:
                        print(f"❌ 无法解析响应")
                        return None
                    
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
    
    def list_tools(self) -> List[Dict]:
        """列出所有可用工具"""
        try:
            headers = self.headers.copy()
            if self.session_id:
                headers["Mcp-Session-Id"] = self.session_id
            
            response = self.client.post(
                self.base_url,
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/list",
                    "params": {}
                }
            )
            
            if response.status_code == 200:
                # 提取 SSE 事件中的数据
                content = response.text
                # 解析 SSE 格式：查找 data: 开头的行
                data = None
                for line in content.split('\n'):
                    if line.startswith('data:'):
                        try:
                            data = json.loads(line[5:].strip())
                            break
                        except:
                            continue
                
                if data is None:
                    try:
                        data = response.json()
                    except:
                        print(f"❌ 无法解析响应")
                        return []
                    
                tools = data.get('result', {}).get('tools', [])
                return tools
            else:
                print(f"❌ 获取工具列表失败：{response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 错误：{e}")
            return []
    
    def get_resource(self, uri: str) -> str:
        """
        获取资源内容
        
        Args:
            uri: 资源 URI
            
        Returns:
            资源内容
        """
        try:
            response = self.client.post(
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
    
    def disconnect(self):
        """断开连接"""
        self.client.close()
        print("👋 已断开连接")
    
    def __enter__(self):
        """上下文管理器进入"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect()


# ==================== 测试函数 ====================

def test_all_tools():
    """测试所有工具"""
    client = MCPClient("http://127.0.0.1:8080")
    
    # 连接服务器
    if not client.connect():
        return
    
    print("\n" + "=" * 60)
    print("获取工具列表...")
    print("=" * 60)
    
    tools = client.list_tools()
    for tool in tools:
        print(f"\n🔧 工具：{tool.get('name')}")
        print(f"   描述：{tool.get('description', '无')}")
    
    print("\n" + "=" * 60)
    print("测试工具调用...")
    print("=" * 60)
    
    # 测试加法
    print("\n➕ 测试加法 (5 + 3):")
    result = client.call_tool("add", {"a": 5, "b": 3})
    print(f"   结果：{result}")
    
    # 测试乘法
    print("\n✖️ 测试乘法 (4 × 7):")
    result = client.call_tool("multiply", {"a": 4, "b": 7})
    print(f"   结果：{result}")
    
    # 测试减法
    print("\n➖ 测试减法 (10 - 3):")
    result = client.call_tool("subtract", {"a": 10, "b": 3})
    print(f"   结果：{result}")
    
    # 测试除法
    print("\n➗ 测试除法 (20 ÷ 4):")
    result = client.call_tool("divide", {"a": 20, "b": 4})
    print(f"   结果：{result}")
    
    # 测试获取资源
    print("\n" + "=" * 60)
    print("测试资源访问...")
    print("=" * 60)
    
    print("\n📚 获取服务器名称:")
    name = client.get_resource("info://server/name")
    print(f"   {name}")
    
    print("\n📚 获取服务器版本:")
    version = client.get_resource("info://server/version")
    print(f"   {version}")
    
    print("\n📚 获取工具列表:")
    tools_info = client.get_resource("info://server/tools")
    print(f"   {tools_info}")
    
    # 断开连接
    client.disconnect()


def simple_demo():
    """简单演示 - 快速调用示例"""
    print("=" * 60)
    print("MCP Client - 简单演示")
    print("=" * 60)
    
    # 使用上下文管理器
    with MCPClient("http://127.0.0.1:8080") as client:
        print("\n快速调用示例:")
        print("-" * 60)
        
        # 调用加法
        result = client.call_tool("add", {"a": 10, "b": 20})
        print(f"10 + 20 = {result}")
        
        # 调用乘法
        result = client.call_tool("multiply", {"a": 6, "b": 7})
        print(f"6 × 7 = {result}")
        
        print("-" * 60)


# ==================== 主函数 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Client - HTTP 传输协议")
    print("=" * 60)
    print("开始测试 MCP 服务器连接...")
    print("=" * 60)
    
    # 运行完整测试
    test_all_tools()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
