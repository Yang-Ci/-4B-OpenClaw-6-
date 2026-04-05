# Audio 项目文件结构

本项目包含音频录制、语音识别、文本转语音和 MCP 服务等相关功能。

## 📁 目录结构

```
e:\audio/
├── config/              # 配置文件
│   ├── activate_env.bat       # 环境激活脚本
│   ├── mcp_config.json        # MCP 配置
│   ├── mcp_config_ui.html     # MCP Web 配置界面
│   └── requirements.txt       # Python 依赖
│
├── docs/                # 文档
│   ├── MCP_CLIENT_GUIDE.md    # MCP Client 使用指南
│   ├── MCP_HTTP_GUIDE.md      # MCP HTTP 模式指南
│   ├── MCP_SETUP_GUIDE.md     # MCP 安装配置指南
│   └── README_MCP_HTTP.md     # MCP HTTP 快速入门
│
├── mcp/                 # MCP 相关代码
│   ├── README.md              # MCP 文件夹说明
│   ├── mcp_client.py          # MCP 异步客户端
│   ├── mcp_client_sync.py     # MCP 同步客户端 (推荐)
│   ├── mcp_server.py          # MCP 基础服务器
│   ├── mcp_server_http.py     # MCP HTTP 服务器
│   └── mcp_server_web.py      # MCP Web 界面服务器
│
├── outputs/             # 音频输出文件
│   ├── edge_output.wav        # Edge TTS 输出
│   ├── mandarin_output.wav    # 普通话输出
│   ├── output.wav             # 录音输出
│   ├── response_cantonese.wav # 粤语响应
│   ├── response_mandarin.wav  # 普通话响应
│   └── ttx_output.wav         # TTS 输出
│
├── src/                 # 源代码
│   ├── python/                # Python 源码
│   │   ├── audio_receive.py       # 录音程序 (Python 版)
│   │   ├── edge_tts_cantonese.py  # 粤语 TTS
│   │   ├── edge_tts_mandarin.py   # 普通话 TTS
│   │   ├── edge_tts_tool.py       # TTS 工具
│   │   ├── ppttxs3.py             # PPT 转 TTS
│   │   ├── qwen_API.py            # 通义千问 API
│   │   ├── voice_assistant.py     # 语音助手 (C++ 版)
│   │   ├── voice_assistant_01.py  # 语音助手 (Python 版)
│   │   ├── voice_command_mcp.py   # 语音指令助手 (MCP 版) ⭐ 新增
│   │   └── whisper_asr.py         # Whisper 语音识别
│   │
│   └── audio_receive.cpp      # 录音程序 (C++ 版)
│   └── audio_receive.exe      # 录音程序编译文件
│
└── __pycache__/         # Python 缓存
```

## 🚀 快速开始

### 1. 环境配置

```bash
# 激活 conda 环境
conda activate voice_assistant_env

# 或使用脚本
config\activate_env.bat
```

### 2. 运行语音助手

```bash
# Python 版本
python src\python\voice_assistant_01.py

# C++ 版本 (需要先编译)
src\audio_receive.exe
```

### 3. 运行 MCP 服务

```bash
# 启动服务器
python mcp\mcp_server_web.py

# 使用客户端
python mcp\mcp_client_sync.py
```

## 📦 功能模块

### 音频录制
- `src/audio_receive.cpp` - C++ 版录音程序
- `src/python/audio_receive.py` - Python 版录音程序

### 语音识别 (ASR)
- `src/python/whisper_asr.py` - Whisper 模型语音识别

### 文本转语音 (TTS)
- `src/python/edge_tts_cantonese.py` - 粤语 TTS
- `src/python/edge_tts_mandarin.py` - 普通话 TTS
- `src/python/edge_tts_tool.py` - TTS 工具函数

### 大模型 API
- `src/python/qwen_API.py` - 通义千问 API 调用

### 语音助手
- `src/python/voice_assistant.py` - 完整语音助手 (C++ 录音版)
- `src/python/voice_assistant_01.py` - 完整语音助手 (Python 录音版)
- `src/python/voice_command_mcp.py` - 语音指令助手 (MCP 版) ⭐ **新增**

### MCP 服务
- `mcp/` - MCP 服务器和客户端

## 🔧 依赖安装

```bash
pip install -r config\requirements.txt
```

主要依赖:
- pyaudio - 音频录制
- openai-whisper - 语音识别
- edge-tts - 文本转语音
- dashscope - 通义千问 API
- fastmcp - MCP 服务
- flask - Web 服务
- httpx - HTTP 客户端

## 📝 使用示例

### 录音
```bash
python src\python\audio_receive.py
```

### 语音识别
```bash
python src\python\whisper_asr.py
```

### 文本转语音
```bash
python src\python\edge_tts_mandarin.py
python src\python\edge_tts_cantonese.py
```

### 语音助手
```bash
python src\python\voice_assistant_01.py
```

### MCP 服务
```bash
# 终端 1: 启动服务器
python mcp\mcp_server_web.py

# 终端 2: 运行客户端
python mcp\mcp_client_sync.py
```

### 语音指令助手 (MCP 版) ⭐ 新增
```bash
# 终端 1: 启动 MCP Server
python mcp\mcp_server_web.py

# 终端 2: 运行语音指令助手
python src\python\voice_command_mcp.py

# 操作：按 R 录音 → 说话 → 按 S 停止并处理
# 示例指令："计算 5 加 3"、"10 乘以 7"
```

## 📚 文档

- [MCP Client 使用指南](docs/MCP_CLIENT_GUIDE.md)
- [MCP HTTP 模式指南](docs/MCP_HTTP_GUIDE.md)
- [MCP 安装配置指南](docs/MCP_SETUP_GUIDE.md)
- [MCP 快速入门](docs/README_MCP_HTTP.md)
- [语音指令助手指南](docs/VOICE_COMMAND_MCP_GUIDE.md) ⭐ **新增**

---

**更新日期**: 2026-03-26
