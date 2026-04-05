#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音指令助手 - MCP 版本
流程：语音输入 → 语音识别 → 大模型解析 → MCP Server 工具调用
"""

import os
import sys

# 强制输出立即刷新（解决 Windows 缓冲问题）
os.environ['PYTHONUNBUFFERED'] = '1'

import time
import wave
import json
import threading
import warnings
from typing import Optional, Dict, Any

warnings.filterwarnings("ignore")

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
mcp_dir = os.path.join(project_root, 'mcp')
sys.path.insert(0, mcp_dir)

# 设置 ffmpeg 路径
FFMPEG_PATH = r"C:\Users\Administrator\ffmpeg-2026-03-22-git-9c63742425-essentials_build\ffmpeg-2026-03-22-git-9c63742425-essentials_build\bin"
if os.path.exists(FFMPEG_PATH):
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ.get("PATH", "")

# 导入依赖
try:
    import pyaudio
    import whisper
    from dashscope import Generation
    from http import HTTPStatus
    from mcp_client_sync import MCPClient
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("正在安装依赖...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pyaudio", "openai-whisper", "dashscope", "httpx"])
    print("依赖安装完成，请重新运行程序")
    sys.exit(1)

# ==================== 配置 ====================

# 音频配置
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 1024
BITS_PER_SAMPLE = 16

# Whisper 模型配置
WHISPER_MODEL = "small"
WHISPER_LANGUAGE = "zh"

# Qwen API 配置
QWEN_API_KEY = "sk-8b65dfd067f44a629e8b8965fb2d285a"
QWEN_MODEL = "qwen-turbo"

# MCP Server 配置
MCP_SERVER_URL = "http://127.0.0.1:8081"

# ==================== 录音模块 ====================

class AudioRecorder:
    """音频录音器"""
    
    def __init__(self):
        self.is_recording = False
        self.should_stop = False
        self.audio_data = []
        self.record_thread = None
        self.audio = None
        self.stream = None
        
    def initialize(self):
        """初始化音频设备"""
        try:
            self.audio = pyaudio.PyAudio()
            default_device = self.audio.get_default_input_device_info()
            print(f"✅ 使用设备：{default_device['name']}")
            return True
        except Exception as e:
            print(f"❌ 初始化失败：{e}")
            return False
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            return
        
        self.audio_data = []
        self.should_stop = False
        self.is_recording = True
        
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            self.record_thread = threading.Thread(target=self._record_loop)
            self.record_thread.start()
            print("🎤 正在录音中... (按 S 停止)")
            
        except Exception as e:
            print(f"❌ 开始录音失败：{e}")
            self.is_recording = False
    
    def _record_loop(self):
        """录音循环"""
        while not self.should_stop:
            try:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                self.audio_data.append(data)
            except Exception as e:
                print(f"录音错误：{e}")
                break
    
    def stop_recording(self):
        """停止录音"""
        if not self.is_recording:
            return
        
        self.should_stop = True
        
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join()
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        self.is_recording = False
        print("⏹️ 录音已停止")
    
    def save_to_wav(self, filename):
        """保存为 WAV 文件"""
        if not self.audio_data:
            return False
        
        try:
            audio_bytes = b''.join(self.audio_data)
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_bytes)
            wf.close()
            
            duration = len(self.audio_data) * CHUNK / SAMPLE_RATE
            print(f"💾 录音已保存：{filename} ({duration:.2f}秒)")
            return True
            
        except Exception as e:
            print(f"❌ 保存失败：{e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        if self.stream:
            self.stream.close()
        if self.audio:
            self.audio.terminate()


# ==================== 语音识别模块 ====================

class SpeechRecognizer:
    """语音识别器"""
    
    def __init__(self, model_name="small", language="zh"):
        self.model_name = model_name
        self.language = language
        self.model = None
        
    def load_model(self):
        """加载模型"""
        print(f"🔄 加载 Whisper 模型: {self.model_name}")
        self.model = whisper.load_model(self.model_name)
        print("✅ 模型加载完成")
        
    def transcribe(self, audio_path):
        """语音识别"""
        if not self.model:
            self.load_model()
        
        print(f"🔍 正在识别语音...")
        result = self.model.transcribe(
            audio_path,
            language=self.language,
            verbose=False
        )
        
        text = result["text"].strip()
        print(f"📝 识别结果：{text}")
        return text


# ==================== 大模型模块 ====================

class QwenModel:
    """通义千问大模型"""
    
    def __init__(self, api_key, model="qwen-turbo"):
        self.api_key = api_key
        self.model = model
        
    def chat(self, prompt, system_prompt=None):
        """对话"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = Generation.call(
            model=self.model,
            messages=messages,
            api_key=self.api_key,
            result_format='message'
        )
        
        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0].message.content
        else:
            print(f"❌ 大模型调用失败：{response.message}")
            return None


# ==================== MCP 工具调用模块 ====================

class MCPToolCaller:
    """MCP 工具调用器"""
    
    def __init__(self, server_url):
        self.server_url = server_url
        self.client = MCPClient(server_url)
        self.connected = False
        
    def connect(self):
        """连接到 MCP Server"""
        self.connected = self.client.connect()
        if self.connected:
            print(f"✅ 已连接到 MCP Server: {self.server_url}")
        else:
            print(f"❌ 无法连接到 MCP Server: {self.server_url}")
        return self.connected
    
    def disconnect(self):
        """断开连接"""
        if self.connected:
            self.client.disconnect()
            self.connected = False
            print("👋 已断开 MCP Server 连接")
    
    def get_available_tools(self):
        """获取可用工具列表"""
        if not self.connected:
            return []
        
        tools = self.client.list_tools()
        return tools
    
    def call_tool(self, tool_name, arguments):
        """调用工具"""
        if not self.connected:
            print("❌ 未连接到 MCP Server")
            return None
        
        try:
            result = self.client.call_tool(tool_name, arguments)
            print(f"✅ 工具调用成功：{tool_name}({arguments}) = {result}")
            return result
        except Exception as e:
            print(f"❌ 工具调用失败：{e}")
            return None


# ==================== 智能指令处理器 ====================

class VoiceCommandProcessor:
    """语音指令处理器"""
    
    def __init__(self):
        self.recorder = AudioRecorder()
        self.recognizer = SpeechRecognizer(WHISPER_MODEL, WHISPER_LANGUAGE)
        self.qwen = QwenModel(QWEN_API_KEY, QWEN_MODEL)
        self.mcp = MCPToolCaller(MCP_SERVER_URL)
        
    def initialize(self):
        """初始化所有组件"""
        print("=" * 60)
        print("        语音指令助手 - MCP 版本")
        print("=" * 60)
        print()
        
        # 初始化录音设备
        if not self.recorder.initialize():
            return False
        
        # 加载语音识别模型
        self.recognizer.load_model()
        
        # 连接到 MCP Server
        if not self.mcp.connect():
            print("⚠️ MCP Server 未启动，部分功能可能不可用")
            print("   请先运行：python mcp/mcp_server_web.py")
        else:
            # 显示可用工具
            tools = self.mcp.get_available_tools()
            if tools:
                print(f"\n可用工具：")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool.get('description', '无描述')}")
        
        print()
        return True
    
    def process_command(self, text):
        """处理语音指令"""
        print(f"\n{'=' * 60}")
        print(f"处理指令：{text}")
        print(f"{'=' * 60}\n")
        
        # 构建系统提示词
        system_prompt = """你是一个智能助手，可以理解用户的语音指令并调用相应的工具。

可用的工具有：
1. add(a, b) - 两数相加
2. multiply(a, b) - 两数相乘
3. subtract(a, b) - 两数相减
4. divide(a, b) - 两数相除

当用户说类似以下指令时，你需要识别意图并返回 JSON 格式的工具调用信息：
- "计算 5 加 3" → {"tool": "add", "args": {"a": 5, "b": 3}}
- "帮我算一下 10 乘以 7" → {"tool": "multiply", "args": {"a": 10, "b": 7}}
- "100 减去 37 等于多少" → {"tool": "subtract", "args": {"a": 100, "b": 37}}
- "144 除以 12" → {"tool": "divide", "args": {"a": 144, "b": 12}}

如果用户的指令不涉及计算，请直接回答用户的问题。

请只返回 JSON 数据或直接回答，不要添加额外的解释。"""
        
        # 调用大模型
        print("🤖 正在分析指令...")
        response = self.qwen.chat(text, system_prompt)
        
        if not response:
            print("❌ 大模型分析失败")
            return None
        
        print(f"📊 大模型响应：{response}")
        
        # 尝试解析为 JSON
        try:
            # 提取 JSON 部分
            if '{' in response and '}' in response:
                json_start = response.index('{')
                json_end = response.rindex('}') + 1
                json_str = response[json_start:json_end]
                
                tool_call = json.loads(json_str)
                
                # 调用 MCP 工具
                if 'tool' in tool_call and 'args' in tool_call:
                    tool_name = tool_call['tool']
                    arguments = tool_call['args']
                    
                    print(f"\n🔧 调用 MCP 工具：{tool_name}({arguments})")
                    
                    if self.mcp.connected:
                        result = self.mcp.call_tool(tool_name, arguments)
                        
                        if result is not None:
                            print(f"\n✅ 执行结果：{result}")
                            
                            # 让大模型用自然语言解释结果
                            explain_prompt = f"用户问：{text}\n计算结果是：{result}\n请用简洁的中文回答用户。"
                            explanation = self.qwen.chat(explain_prompt)
                            
                            if explanation:
                                print(f"\n💬 {explanation}")
                            
                            return result
                    else:
                        print("❌ MCP Server 未连接，无法调用工具")
                        return None
        
        except json.JSONDecodeError:
            # 不是 JSON 格式，直接返回大模型的回答
            print(f"\n💬 {response}")
            return response
        
        except Exception as e:
            print(f"❌ 处理失败：{e}")
            return None
        
        return response
    
    def run(self):
        """运行主循环"""
        print("🎤 准备就绪！按 R 开始录音，按 S 停止录音并处理")
        print("=" * 60)
        print("💡 提示：程序正在等待您的按键输入...")
        print("   按 R 键 → 开始录音")
        print("   按 S 键 → 停止录音并处理")
        print("   按 Q 键 → 退出程序")
        print("=" * 60)
        sys.stdout.flush()
        
        try:
            while True:
                if sys.platform == 'win32':
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').lower()
                        
                        if key == 'r':
                            if not self.recorder.is_recording:
                                self.recorder.start_recording()
                                sys.stdout.flush()
                        
                        elif key == 's':
                            if self.recorder.is_recording:
                                self.recorder.stop_recording()
                                sys.stdout.flush()
                                
                                audio_file = "temp_command.wav"
                                if self.recorder.save_to_wav(audio_file):
                                    text = self.recognizer.transcribe(audio_file)
                                    
                                    if text:
                                        self.process_command(text)
                                    
                                    try:
                                        os.remove(audio_file)
                                    except:
                                        pass
                                
                                print("\n" + "=" * 60)
                                print("🎤 准备就绪！按 R 开始录音，按 S 停止录音并处理")
                                print("=" * 60)
                                sys.stdout.flush()
                        
                        elif key == 'q':
                            print("\n👋 退出程序...")
                            sys.stdout.flush()
                            break
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n👋 程序中断")
        
        finally:
            # 清理资源
            if self.recorder.is_recording:
                self.recorder.stop_recording()
            self.recorder.cleanup()
            self.mcp.disconnect()
            print("✅ 资源已清理")


# ==================== 主函数 ====================

def main():
    """主函数"""
    processor = VoiceCommandProcessor()
    
    if processor.initialize():
        processor.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
