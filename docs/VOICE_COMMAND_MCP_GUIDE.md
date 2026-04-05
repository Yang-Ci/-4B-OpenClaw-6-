# 语音指令助手 - MCP 版本

## 📋 功能说明

这是一个完整的语音指令处理系统，实现了以下流程：

```
语音输入 → 语音识别 → 大模型解析 → MCP Server 工具调用
```

## 🚀 快速开始

### 1. 启动 MCP Server

首先需要启动 MCP Server（在一个终端中）：

```bash
conda activate voice_assistant_env
python mcp\mcp_server_web.py
```

服务器会运行在 `http://127.0.0.1:8081`

### 2. 运行语音指令助手

在另一个终端中运行：

```bash
conda activate voice_assistant_env
python src\python\voice_command_mcp.py
```

## 🎯 使用方法

### 操作步骤

1. **按 R 键** - 开始录音
2. **说出指令** - 例如："计算 5 加 3"
3. **按 S 键** - 停止录音并处理
4. **查看结果** - 系统会自动识别、分析并调用工具

### 支持的指令示例

#### 数学计算
- "计算 5 加 3"
- "帮我算一下 10 乘以 7"
- "100 减去 37 等于多少"
- "144 除以 12"

#### 普通对话
- "你好"
- "今天天气怎么样"
- "讲个笑话"

## 🔧 技术架构

### 模块组成

```
voice_command_mcp.py
├── AudioRecorder        # 录音模块
├── SpeechRecognizer     # 语音识别模块 (Whisper)
├── QwenModel           # 大模型模块 (通义千问)
├── MCPToolCaller       # MCP 工具调用模块
└── VoiceCommandProcessor # 指令处理器
```

### 数据流程

```
┌─────────────┐
│  语音输入   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  录音保存   │ (AudioRecorder)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  语音识别   │ (Whisper)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  文本输出   │ "计算 5 加 3"
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  大模型分析 │ (Qwen)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  JSON 解析  │ {"tool": "add", "args": {"a": 5, "b": 3}}
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MCP 调用   │ (MCPToolCaller)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  结果返回   │ 8
└─────────────┘
```

## 📝 配置说明

### 音频配置

```python
SAMPLE_RATE = 16000      # 采样率
CHANNELS = 1             # 声道数
CHUNK = 1024             # 缓冲区大小
```

### Whisper 配置

```python
WHISPER_MODEL = "small"  # 模型大小: tiny/base/small/medium/large
WHISPER_LANGUAGE = "zh"  # 语言: zh (中文)
```

### Qwen 配置

```python
QWEN_API_KEY = "your-api-key"  # 通义千问 API Key
QWEN_MODEL = "qwen-turbo"      # 模型名称
```

### MCP Server 配置

```python
MCP_SERVER_URL = "http://127.0.0.1:8081"  # MCP Server 地址
```

## 🛠️ 扩展工具

### 添加新工具

在 `mcp/mcp_server_web.py` 中添加新工具：

```python
@mcp.tool()
def power(base: float, exponent: float) -> float:
    """计算幂运算"""
    result = base ** exponent
    print(f"计算：{base} ^ {exponent} = {result}")
    return result
```

然后在 `voice_command_mcp.py` 中更新系统提示词：

```python
可用的工具有：
1. add(a, b) - 两数相加
2. multiply(a, b) - 两数相乘
3. subtract(a, b) - 两数相减
4. divide(a, b) - 两数相除
5. power(base, exponent) - 幂运算  # 新增
```

## 🎨 示例输出

```
============================================================
        语音指令助手 - MCP 版本
============================================================

✅ 使用设备：麦克风 (Realtek Audio)
🔄 加载 Whisper 模型: small
✅ 模型加载完成
✅ 已连接到 MCP Server: http://127.0.0.1:8081

可用工具：
  - add: 两个数相加
  - multiply: 两个数相乘
  - subtract: 两个数相减
  - divide: 两个数相除

🎤 准备就绪！按 R 开始录音，按 S 停止录音并处理
============================================================

🎤 正在录音中... (按 S 停止)
⏹️ 录音已停止
💾 录音已保存：temp_command.wav (2.34秒)
🔍 正在识别语音...
📝 识别结果：计算 5 加 3

============================================================
处理指令：计算 5 加 3
============================================================

🤖 正在分析指令...
📊 大模型响应：{"tool": "add", "args": {"a": 5, "b": 3}}

🔧 调用 MCP 工具：add({'a': 5, 'b': 3})
✅ 工具调用成功：add({'a': 5, 'b': 3}) = 8

✅ 执行结果：8

💬 5 加 3 等于 8。

============================================================
🎤 准备就绪！按 R 开始录音，按 S 停止录音并处理
============================================================
```

## ⚠️ 注意事项

1. **MCP Server 必须先启动** - 否则工具调用功能不可用
2. **需要网络连接** - 调用通义千问 API 需要联网
3. **首次运行较慢** - Whisper 模型需要下载（约 244MB）
4. **安静环境** - 建议在安静环境下录音，提高识别准确率

## 🔍 故障排查

### 问题 1: MCP Server 连接失败

```
❌ 无法连接到 MCP Server: http://127.0.0.1:8081
```

**解决方案**:
- 确认 MCP Server 已启动
- 检查端口 8081 是否被占用

### 问题 2: 语音识别失败

```
❌ 识别失败: ...
```

**解决方案**:
- 检查 ffmpeg 是否正确安装
- 确认麦克风设备正常工作

### 问题 3: 大模型调用失败

```
❌ 大模型调用失败: ...
```

**解决方案**:
- 检查 API Key 是否正确
- 确认网络连接正常
- 检查 API 配额是否充足

## 📚 相关文件

- [`audio_receive.py`](audio_receive.py) - 录音程序
- [`whisper_asr.py`](whisper_asr.py) - 语音识别
- [`qwen_API.py`](qwen_API.py) - 大模型 API
- [`mcp_server_web.py`](../../mcp/mcp_server_web.py) - MCP Server
- [`mcp_client_sync.py`](../../mcp/mcp_client_sync.py) - MCP Client

---

**更新日期**: 2026-03-26
