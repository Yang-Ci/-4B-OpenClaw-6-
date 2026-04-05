#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server - 带 Web 界面的 HTTP 版本
功能：HTTP 传输协议 + Web 配置界面 + 工具测试
"""

import os
from fastmcp import FastMCP
from flask import Flask, render_template_string, request, jsonify
import threading
import webbrowser
from pathlib import Path

# 设置环境变量
os.environ['FASTMCP_HOST'] = '127.0.0.1'
os.environ['FASTMCP_PORT'] = '8081'

# 创建 MCP 实例
mcp = FastMCP("MCP Server Web")


# ==================== 工具定义 ====================

@mcp.tool()
def add(a: int, b: int) -> int:
    """两个数相加"""
    result = a + b
    print(f"计算：{a} + {b} = {result}")
    return result


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """两个数相乘"""
    result = a * b
    print(f"计算：{a} × {b} = {result}")
    return result


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """两个数相减"""
    result = a - b
    print(f"计算：{a} - {b} = {result}")
    return result


@mcp.tool()
def divide(a: float, b: float) -> float:
    """两个数相除"""
    if b == 0:
        raise ValueError("除数不能为 0")
    result = a / b
    print(f"计算：{a} ÷ {b} = {result}")
    return result


# ==================== Web 界面 ====================

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Server - Web 控制台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
        }
        .status {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #2196F3;
        }
        .tool-section {
            margin-top: 30px;
        }
        .tool-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }
        .tool-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .test-form {
            display: grid;
            grid-template-columns: 1fr 1fr auto;
            gap: 10px;
            margin-top: 15px;
        }
        input {
            padding: 10px;
            border: 2px solid #e9ecef;
            border-radius: 5px;
            font-size: 1em;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .result {
            margin-top: 10px;
            padding: 10px;
            background: #d4edda;
            border-radius: 5px;
            color: #155724;
            display: none;
        }
        .endpoint {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 MCP Server Web 控制台</h1>
        
        <div class="status">
            <strong>✅ 服务器运行中</strong><br>
            地址：http://127.0.0.1:8080<br>
            传输协议：Streamable HTTP
        </div>

        <div class="tool-section">
            <h2>🛠️ 工具测试</h2>
            
            <div class="tool-card">
                <h3>➕ add - 两数相加</h3>
                <div class="test-form">
                    <input type="number" id="add-a" placeholder="a">
                    <input type="number" id="add-b" placeholder="b">
                    <button onclick="testTool('add')">测试</button>
                </div>
                <div class="result" id="add-result"></div>
            </div>

            <div class="tool-card">
                <h3>✖️ multiply - 两数相乘</h3>
                <div class="test-form">
                    <input type="number" id="multiply-a" placeholder="a">
                    <input type="number" id="multiply-b" placeholder="b">
                    <button onclick="testTool('multiply')">测试</button>
                </div>
                <div class="result" id="multiply-result"></div>
            </div>

            <div class="tool-card">
                <h3>➖ subtract - 两数相减</h3>
                <div class="test-form">
                    <input type="number" id="subtract-a" placeholder="a">
                    <input type="number" id="subtract-b" placeholder="b">
                    <button onclick="testTool('subtract')">测试</button>
                </div>
                <div class="result" id="subtract-result"></div>
            </div>

            <div class="tool-card">
                <h3>➗ divide - 两数相除</h3>
                <div class="test-form">
                    <input type="number" id="divide-a" placeholder="a" step="0.1">
                    <input type="number" id="divide-b" placeholder="b" step="0.1">
                    <button onclick="testTool('divide')">测试</button>
                </div>
                <div class="result" id="divide-result"></div>
            </div>
        </div>

        <div class="endpoint">
            <strong>📡 API 端点:</strong><br>
            SSE: http://127.0.0.1:8080/sse<br>
            POST: http://127.0.0.1:8080/message
        </div>
    </div>

    <script>
        async function testTool(toolName) {
            const a = document.getElementById(toolName + '-a').value;
            const b = document.getElementById(toolName + '-b').value;
            const resultDiv = document.getElementById(toolName + '-result');
            
            try {
                const response = await fetch('/api/tool/' + toolName, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({a: parseFloat(a), b: parseFloat(b)})
                });
                
                const data = await response.json();
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<strong>结果:</strong> ' + data.result;
            } catch (error) {
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<strong>错误:</strong> ' + error.message;
                resultDiv.style.background = '#f8d7da';
                resultDiv.style.color = '#721c24';
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Web 控制台首页"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/tool/<tool_name>', methods=['POST'])
def api_tool(tool_name):
    """工具测试 API"""
    data = request.json
    a = data.get('a', 0)
    b = data.get('b', 0)
    
    try:
        if tool_name == 'add':
            result = add(int(a), int(b))
        elif tool_name == 'multiply':
            result = multiply(int(a), int(b))
        elif tool_name == 'subtract':
            result = subtract(int(a), int(b))
        elif tool_name == 'divide':
            result = divide(float(a), float(b))
        else:
            return jsonify({'error': 'Unknown tool'}), 400
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 主函数 ====================

def run_web_server():
    """运行 Web 服务器"""
    app.run(host='127.0.0.1', port=5000, debug=False)


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Server - Web 控制台版本")
    print("=" * 60)
    print("MCP 服务器地址：http://127.0.0.1:8081")
    print("Web 控制台地址：http://127.0.0.1:5000")
    print("=" * 60)
    
    # 启动 Web 服务器线程
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # 自动打开浏览器
    import time
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:5000')
    
    print("已自动打开浏览器...")
    print("=" * 60)
    
    # 启动 MCP Server，指定端口
    import uvicorn
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8081)
