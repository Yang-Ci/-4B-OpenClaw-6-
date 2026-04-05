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
├── openclaw_controller/ # ROS2 机械臂控制包 ⭐ 新增
│   ├── openclaw_controller/   # 核心功能模块
│   │   ├── voice_openclaw.py         # 语音交互节点
│   │   ├── track_and_grab_node.py    # 视觉抓取节点
│   │   ├── feishu_sender.py          # 飞书消息发送
│   │   └── config.py                 # 配置文件
│   ├── launch/                # 启动文件
│   ├── config/                # 配置文件
│   ├── scripts/               # 脚本文件
│   └── README.md              # 详细文档
│
├── software/            # 可视化工具集 ⭐ 新增
│   ├── armpi_pro_control/     # 机械臂控制界面 (PyQt5)
│   │   ├── main.py                   # 主程序
│   │   ├── servo_controller.py       # 舵机控制器
│   │   └── ui.py                     # 界面文件
│   ├── lab_config/            # 实验室配置工具
│   │   ├── main.py                   # 主程序
│   │   ├── lab_config_proxy.py       # 配置代理
│   │   └── add_color_dialog.py       # 颜色添加对话框
│   └── servo_tool/            # 舵机调试工具
│       ├── main.py                   # 主程序
│       └── servo_controller.py       # 舵机控制器
│
├── ros_ws/              # ROS 工作空间 ⭐ 新增
│   └── src/
│       ├── armpi_remote_control/     # 远程控制功能包
│       │   ├── scripts/              # Python 脚本
│       │   │   ├── servo_gui_tkinter.py  # 图形化GUI
│       │   │   └── read_servo_state.py   # 状态读取
│       │   ├── launch/               # 启动文件
│       │   ├── msg/                  # 消息定义
│       │   └── README.md             # 详细文档
│       ├── armpi_pro_kinematics/     # 运动学解算
│       ├── armpi_pro_common/         # 公共模块
│       ├── hiwonder_servo_controllers/ # 舵机控制器
│       ├── color_tracking/           # 颜色追踪
│       └── visual_processing/        # 视觉处理
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

### 4. 运行机械臂控制 ⭐ 新增

```bash
# 可视化工具
cd software/armpi_pro_control
python main.py

# ROS 远程控制
roslaunch armpi_remote_control gui_tkinter.launch

# ROS2 语音交互
ros2 launch openclaw_controller start.launch.py
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

### 🤖 OpenClaw Controller (ROS2) ⭐ 新增
基于ROS2的机械臂语音交互与视觉抓取控制包，适用于树莓派4B平台的6自由度机械臂。

**核心功能：**
- **语音交互闭环**：语音唤醒 → ASR识别 → 大模型处理 → TTS播报
- **视觉抓取系统**：颜色识别 → 深度定位 → 机械臂抓取
- **远程消息推送**：支持飞书消息实时推送
- **多节点协同**：ROS2节点间通信与状态同步

**主要节点：**
- `voice_openclaw.py` - 语音交互节点
- `track_and_grab_node.py` - 视觉抓取节点
- `feishu_sender.py` - 飞书消息发送

**详细文档：** [openclaw_controller/README.md](openclaw_controller/README.md)

### 🖥️ Software 可视化工具集 ⭐ 新增
提供图形化界面工具，用于机械臂控制、配置和调试。

#### 1. armpi_pro_control - 机械臂控制界面
- **技术栈**：PyQt5
- **功能**：
  - 6个舵机的滑块控制（0-1000范围）
  - 动作组管理和执行
  - 实时舵机状态显示
  - 一键回到中位功能
- **启动方式**：
  ```bash
  cd software/armpi_pro_control
  python main.py
  ```

#### 2. lab_config - 实验室配置工具
- **功能**：
  - 颜色识别范围配置（LAB色彩空间）
  - 实时摄像头画面显示
  - 颜色参数保存和加载
- **启动方式**：
  ```bash
  cd software/lab_config
  python main.py
  ```

#### 3. servo_tool - 舵机调试工具
- **功能**：
  - 单个舵机调试
  - 舵机状态读取
  - 舵机参数配置
- **启动方式**：
  ```bash
  cd software/servo_tool
  python main.py
  ```

### 🌐 ROS 远程控制 ⭐ 新增
基于ROS1的远程控制功能包，支持通过WiFi远程控制机械臂。

**核心功能：**
- **图形化界面控制**（Python Tkinter）
- **命令行界面控制**
- **实时读取舵机状态**
- **远程控制6个舵机**

**主要组件：**
- `servo_gui_tkinter.py` - 图形化GUI
- `servo_state_publisher.cpp` - 状态发布器
- `servo_command_receiver.cpp` - 命令接收器

**启动方式：**
```bash
# 图形化GUI
roslaunch armpi_remote_control gui_tkinter.launch

# 命令行GUI
roslaunch armpi_remote_control gui.launch
```

**详细文档：** [ros_ws/src/armpi_remote_control/README.md](ros_ws/src/armpi_remote_control/README.md)

**ROS工作空间包含：**
- `armpi_pro_kinematics/` - 运动学解算
- `armpi_pro_common/` - 公共模块
- `hiwonder_servo_controllers/` - 舵机控制器
- `color_tracking/` - 颜色追踪
- `visual_processing/` - 视觉处理

## 🔧 依赖安装

### Python 依赖
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

### ROS 依赖 ⭐ 新增

#### ROS1 (远程控制)
```bash
# Ubuntu 20.04
sudo apt install ros-noetic-desktop

# 编译工作空间
cd ros_ws
catkin_make
source devel/setup.bash
```

#### ROS2 (OpenClaw Controller)
```bash
# Ubuntu 22.04
sudo apt install ros-humble-desktop

# 编译工作空间
cd ros_ws
colcon build
source install/setup.bash
```

### PyQt5 依赖 (可视化工具) ⭐ 新增
```bash
pip install PyQt5 opencv-python numpy
```

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

### 机械臂控制 ⭐ 新增

#### OpenClaw Controller (ROS2)
```bash
# 启动语音交互节点
ros2 launch openclaw_controller start.launch.py

# 启动视觉抓取节点
ros2 launch openclaw_controller smart_factory.launch.py
```

#### 可视化工具
```bash
# 机械臂控制界面
cd software/armpi_pro_control
python main.py

# 实验室配置工具
cd software/lab_config
python main.py

# 舵机调试工具
cd software/servo_tool
python main.py
```

#### ROS 远程控制
```bash
# 图形化GUI
roslaunch armpi_remote_control gui_tkinter.launch

# 命令行GUI
roslaunch armpi_remote_control gui.launch
```

## 📚 文档

### MCP 相关文档
- [MCP Client 使用指南](docs/MCP_CLIENT_GUIDE.md)
- [MCP HTTP 模式指南](docs/MCP_HTTP_GUIDE.md)
- [MCP 安装配置指南](docs/MCP_SETUP_GUIDE.md)
- [MCP 快速入门](docs/README_MCP_HTTP.md)
- [语音指令助手指南](docs/VOICE_COMMAND_MCP_GUIDE.md)

### 机械臂控制文档 ⭐ 新增
- [OpenClaw Controller 详细文档](openclaw_controller/README.md) - ROS2 机械臂控制包
- [ROS 远程控制详细文档](ros_ws/src/armpi_remote_control/README.md) - ROS1 远程控制功能包
- [ArmPi Pro API 接口说明](ArmPi%20Pro%20API接口说明.md) - 机械臂API文档 

---

**更新日期**: 2026-04-05

**项目仓库**: [GitHub - 4B-OpenClaw-6-](https://github.com/Yang-Ci/-4B-OpenClaw-6-)
