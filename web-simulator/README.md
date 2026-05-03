# ArmPi Pro Robot Simulator

ArmPi Pro 机械臂 Web 仿真器，基于 Three.js 和 URDF 模型，在浏览器中实时展示和控制 6-DOF 机械臂运动。

## 环境要求

- **Node.js** >= 14.x（推荐 18.x LTS）
- **npm** >= 6.x

## 快速开始

### 1. 安装依赖

双击 `install.bat`，自动检查 Node.js 环境并安装项目依赖。

### 2. 启动服务器

双击 `run.bat`，自动启动服务器并打开浏览器访问 `http://localhost:3000`。
在  PS E:\ArmPi\web-simulator cd e:\ArmPi\web-simulator; node server.js
### 3. 手动启动

```bash
npm install
npm start
```

## 项目结构

```
web-simulator/
├── public/
│   ├── index.html          # 主页面（UI 结构、样式、多语言翻译）
│   ├── js/
│   │   └── main.js         # 核心逻辑（Three.js 场景、URDF 加载、关节控制、IK、拖拽）
│   └── lib/
│       ├── three.min.js        # Three.js 引擎
│       ├── three-r128.min.js   # Three.js r128 备用版本
│       ├── STLLoader.js        # STL 模型加载器
│       └── STLLoader-umd.js    # STL 加载器 UMD 版本
├── server.js               # Express 服务器
├── config.json             # 配置文件
├── package.json            # 项目依赖
├── install.bat             # 一键安装依赖
└── run.bat                 # 一键启动服务器
```

## 配置文件

`config.json` 可配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `server.port` | 服务器端口 | `3000` |
| `server.host` | 服务器地址 | `localhost` |
| `robot.urdfPath` | URDF 模型路径 | `../src/armpi_fpv_descrption` |
| `robot.urdfFile` | URDF 文件名 | `urdf/armpi_fpv.urdf` |
| `robot.meshesPath` | 网格文件目录 | `meshes` |
| `display.cameraPosition` | 相机初始位置 | `{x: -0.34, y: 0.25, z: -0.5}` |
| `display.robotRotationX` | 模型 X 轴旋转（弧度） | `-1.5708` (-90°) |
| `display.robotPositionY` | 模型 Y 轴偏移 | `0.02` |
| `display.defaultLanguage` | 默认语言 | `zh` |

## 功能特性

### 3D 可视化
- 基于 URDF 模型加载真实机械臂结构
- 实时 3D 渲染，支持阴影和光照
- 摄像头坐标实时显示（左下角）

### 关节控制
- **滑块控制**：独立调节 6 个关节角度（Base / Shoulder / Elbow / Wrist 1 / Wrist 2 / Gripper）
- **默认姿态**：0° / 5° / 65° / 30° / 0° / 0°
- **启动动画**：从全零姿态平滑过渡到默认姿态（easeInOutCubic 缓动）
- **重置关节**：一键恢复所有关节到默认姿态

### 拖动模式（逆运动学）
- 点击 **拖动模式** 按钮激活
- 拖拽蓝色标记实时控制末端执行器位置
- 基于 Jacobian 矩阵 + 阻尼伪逆的伺服控制器，实现跟手拖动
- 松手后：红色实体 → 紫色虚影 → 平滑动画过渡到目标姿态 → 恢复红色实体

### 轨迹生成
- 点击 **轨迹生成** 按钮
- 从默认姿态平滑动画过渡到当前滑块设定的姿态
- 动画过程：红色实体 → 紫色虚影 → 动画 → 恢复红色实体

### 演示动画
- 点击 **演示动画** 按钮播放预设关节运动轨迹
- 再次点击停止演示

### 多语言支持
- 中文 / English 一键切换
- 所有 UI 文本、按钮、提示均支持双语

### 侧边栏
- 可折叠控制面板，点击侧边栏顶部按钮收起/展开

## 操作说明

| 操作 | 说明 |
|------|------|
| 左键拖动 | 旋转视角 |
| 滚轮 | 缩放 |
| 右键拖动 | 平移视角 |
| 右侧滑块 | 控制各关节角度 |
| 拖动模式 | 拖拽末端执行器（逆运动学解算） |
| 轨迹生成 | 默认姿态 → 当前滑块姿态动画 |
| 演示动画 | 播放/停止预设演示动画 |
| 重置关节 | 复位所有关节到默认姿态 |
| 语言切换 | 中文 / English |

## API 端点

| 端点 | 说明 |
|------|------|
| `GET /api/config` | 获取配置信息 |
| `GET /api/urdf` | 获取 URDF 模型数据 |

## 技术栈

- **Three.js** - 3D 渲染引擎
- **URDFLoader** - URDF 机器人模型加载
- **Express** - Web 服务器
- **Jacobian 逆运动学** - 阻尼伪逆 + P 控制器实现实时伺服
