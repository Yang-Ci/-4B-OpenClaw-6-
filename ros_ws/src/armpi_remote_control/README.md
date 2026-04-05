# ArmPi 远程控制功能包使用文档

## 📋 功能包概述

`armpi_remote_control` 是一个用于远程控制 ArmPi Pro 机械臂的 ROS1 功能包，提供了图形化界面和命令行两种控制方式，支持通过 WiFi 远程控制机械臂的舵机。

### 主要功能
- ✅ 图形化界面控制（Python Tkinter）
- ✅ 命令行界面控制
- ✅ 实时读取舵机状态
- ✅ 远程控制6个舵机
- ✅ 支持设置单个/多个舵机位置
- ✅ 支持回到中位功能
- ✅ 支持停止所有舵机

## 🚀 快速开始

### 1. 编译功能包

```bash
# 进入工作空间
cd /home/ubuntu/armpi_pro

# 编译功能包
catkin_make

# 加载环境
source devel/setup.zsh
```

### 2. 启动远程控制（带图形化界面）

```bash
# 启动图形化GUI
roslaunch armpi_remote_control gui_tkinter.launch
```

### 3. 启动远程控制（命令行）

```bash
# 启动命令行GUI
roslaunch armpi_remote_control gui.launch
```

## 📱 图形化界面使用说明

### 界面布局
- **标题栏**：显示 "ArmPi Servo Control"
- **滑块控制区**：6个舵机的滑块控制器（0-1000范围）
- **按钮区**：
  - `Set Position`：发送当前滑块位置到舵机
  - `Home Position`：所有舵机回到中位（500）
  - `Stop All`：停止所有舵机
- **状态栏**：显示当前状态信息

### 使用流程
1. **停止舵机**：点击 "Stop All" 按钮
2. **调节滑块**：拖动滑块到目标位置
3. **发送命令**：点击 "Set Position" 按钮
4. **观察效果**：舵机会移动到滑块指定的位置
5. **回到中位**：点击 "Home Position" 按钮

### 界面特点
- **实时状态**：位置显示会实时更新
- **滑块锁定**：调节滑块时不会被状态更新覆盖
- **一键操作**：快速设置所有舵机

## ⌨️ 命令行界面使用说明

### 菜单选项
1. `Set single servo position` - 设置单个舵机位置
2. `Set multiple servos position` - 设置多个舵机位置
3. `Reset to home position` - 回到中位
4. `Stop all servos` - 停止所有舵机
5. `Show servo status` - 显示舵机状态
6. `Exit` - 退出

### 使用示例

#### 设置单个舵机
```
Select option: 1
Enter servo ID (1-6): 1
Enter position (0-1000): 300
Enter duration (ms): 500
Servo 1 → Position 300 (500 ms)
```

#### 显示舵机状态
```
Select option: 5
=== Servo Status ===
ID  Position  Temp(c)  Voltage(Y)
1   300       25       6.0
2   500       25       6.0
3   500       25       6.0
4   500       25       6.0
5   500       25       6.0
6   500       25       6.0
```

## 🔧 功能包结构

```
armpi_remote_control/
├── CMakeLists.txt          # 编译配置文件
├── package.xml             # 包信息和依赖
├── include/                # 头文件
│   └── armpi_remote_control/
├── src/                    # 源码
│   ├── servo_state_publisher.cpp    # 状态发布器
│   ├── servo_command_receiver.cpp   # 命令接收器
│   └── remote_gui_node.cpp          # 命令行GUI
├── scripts/                # 脚本
│   ├── read_servo_state.py          # 状态读取脚本
│   └── servo_gui_tkinter.py         # 图形化GUI
├── launch/                 # 启动文件
│   ├── gui.launch                   # 命令行GUI启动
│   ├── gui_tkinter.launch           # 图形化GUI启动
│   └── remote_control.launch        # 远程控制启动
├── msg/                    # 消息定义
│   ├── ServoControl.msg             # 控制消息
│   └── ServoStateFull.msg           # 状态消息
└── config/                 # 配置文件
    └── servo_config.yaml            # 舵机配置
```

## 📡 话题说明

### 发布的话题
- `/armpi_remote/servo_states` - 发布舵机状态（ServoStateFull）
- `/joint_states` - 发布关节状态（sensor_msgs/JointState）

### 订阅的话题
- `/armpi_remote/servo_control` - 接收控制命令（ServoControl）
- `/servo_controllers/port_id_1/servo_states` - 接收实际舵机状态

### 控制消息格式（ServoControl）
```
Header header
uint8[] servo_ids
uint16[] positions
uint16[] durations
bool save_deviation
```

### 状态消息格式（ServoStateFull）
```
Header header
uint8 servo_id
uint16 position
int16 deviation
uint8 temperature
uint16 voltage
uint8 temp_limit
uint16 angle_limit_min
uint16 angle_limit_max
uint16 voltage_limit_min
uint16 voltage_limit_max
uint8 torque_state
```

## ⚙️ 配置参数

### servo_state_publisher 节点参数
- `servo_ids` - 舵机ID列表，默认：`[1, 2, 3, 4, 5, 6]`
- `update_rate` - 更新频率，默认：`10.0` Hz

## 🛠️ 故障排除

### 1. GUI无法启动
**症状**：`Cannot locate node [servo_gui_tkinter]`
**解决方案**：确保Python脚本有执行权限
```bash
chmod +x /home/ubuntu/armpi_pro/src/armpi_remote_control/scripts/servo_gui_tkinter.py
```

### 2. 编译错误
**症状**：`AutoMoc error`
**解决方案**：Qt GUI已移除，使用Python Tkinter GUI

### 3. 滑块自动回到原位
**解决方案**：
- 点击 "Stop All" 停止舵机
- 调节滑块到目标位置
- 点击 "Set Position" 发送命令

### 4. 舵机无响应
**检查点**：
- 确认ROS Master运行正常
- 检查话题是否存在：`rostopic list`
- 检查消息是否发布：`rostopic echo /armpi_remote/servo_control`
- 检查状态是否接收：`rostopic echo /servo_controllers/port_id_1/servo_states`



# 🔧 远程控制设置方法

## 📡 远程控制原理

`armpi_remote_control` 功能包通过ROS的网络通信机制实现远程控制，主要原理是：
- 树莓派作为ROS Master运行在局域网中
- 远程电脑作为ROS Client连接到树莓派的ROS Master
- 通过WiFi网络传输控制命令和状态信息

## 🛠️ 远程控制设置步骤

### 1. **网络设置**

#### 方法A：树莓派和远程电脑连接到同一WiFi网络
1. **树莓派**：连接到WiFi网络，获取IP地址
   ```bash
   # 在树莓派终端运行
   ifconfig wlan0
   # 记录IP地址，例如：192.168.1.100
   ```

2. **远程电脑**：连接到同一WiFi网络

#### 方法B：树莓派作为WiFi热点
1. **树莓派**：设置为WiFi热点
   - 参考：[树莓派设置WiFi热点教程](https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-wireless-access-point)
   - 热点IP通常为：192.168.4.1

2. **远程电脑**：连接到树莓派的WiFi热点

### 2. **配置远程电脑的ROS环境**

1. **安装ROS Noetic**（如果未安装）
   - 参考：[ROS Noetic安装教程](http://wiki.ros.org/noetic/Installation/Ubuntu)

2. **设置ROS Master地址**
   ```bash
   # 在远程电脑终端运行（每次启动终端都需要设置）
   export ROS_MASTER_URI=http://树莓派IP:11311
   export ROS_IP=远程电脑IP
   
   # 例如：
   export ROS_MASTER_URI=http://192.168.1.100:11311
   export ROS_IP=192.168.1.101
   ```

3. **验证连接**
   ```bash
   # 查看树莓派上的ROS节点
   rostopic list
   # 如果能看到话题列表，说明连接成功
   ```

### 3. **启动远程控制**

#### 方法1：在远程电脑上运行图形化GUI
1. **复制功能包**（如果远程电脑没有）
   ```bash
   # 从树莓派复制功能包到远程电脑
   scp -r ubuntu@树莓派IP:/home/ubuntu/armpi_pro/src/armpi_remote_control ~/catkin_ws/src/
   
   # 编译
   cd ~/catkin_ws
   catkin_make
   source devel/setup.bash
   ```

2. **启动图形化GUI**
   ```bash
   # 在远程电脑运行
   roslaunch armpi_remote_control gui_tkinter.launch
   ```

#### 方法2：在远程电脑上运行命令行GUI
```bash
# 在远程电脑运行
roslaunch armpi_remote_control gui.launch
```

### 4. **使用远程控制**

#### 图形化界面操作
1. **停止舵机**：点击 "Stop All" 按钮
2. **调节滑块**：拖动滑块到目标位置
3. **发送命令**：点击 "Set Position" 按钮
4. **观察效果**：舵机会移动到指定位置
5. **回到中位**：点击 "Home Position" 按钮

#### 命令行界面操作
1. 选择菜单选项
2. 输入舵机ID和目标位置
3. 观察舵机运动

## 🌐 网络故障排除

### 1. **连接失败**
- **检查网络**：确保树莓派和远程电脑在同一网络
- **检查防火墙**：关闭树莓派和远程电脑的防火墙
- **检查ROS Master**：确保树莓派上的ROS Master正在运行

### 2. **延迟问题**
- **使用有线网络**：如果WiFi延迟高，考虑使用有线网络
- **优化网络**：减少网络干扰，使用5GHz WiFi
- **调整更新频率**：在 `gui_tkinter.launch` 中调整 `update_rate` 参数

### 3. **状态更新问题**
- **检查话题**：确保 `/servo_controllers/port_id_1/servo_states` 话题有数据
- **检查节点**：确保 `servo_state_publisher` 节点正在运行

## 📱 远程控制推荐配置

- **网络**：5GHz WiFi或有线网络
- **远程电脑**：Ubuntu 20.04 + ROS Noetic
- **树莓派**：ArmPi Pro + ROS Noetic
- **ROS Master**：运行在树莓派上
- **控制界面**：Python Tkinter GUI（响应速度快）

## 🎯 远程控制优势

- **无需物理接触**：可以在局域网内任何位置控制机械臂
- **直观操作**：图形化界面易于使用
- **实时反馈**：实时显示舵机状态
- **多设备支持**：支持多个远程设备同时控制

现在你可以通过以上方法实现对ArmPi Pro机械臂的远程控制了！如果遇到问题，请参考文档中的故障排除部分。

## 📝 版本信息

### 功能包版本
- **版本**：1.0.0
- **ROS版本**：ROS1 Noetic
- **支持平台**：Ubuntu 20.04 / Raspberry Pi OS

### 依赖项
- `roscpp`
- `rospy`
- `std_msgs`
- `sensor_msgs`
- `message_generation`
- `hiwonder_servo_msgs`
- `Python 3.8+`
- `Tkinter`

## 🔗 相关资源

- **ROS Wiki**：http://wiki.ros.org/
- **ArmPi Pro 文档**：https://www.hiwonder.com/
- **Hiwonder Servo SDK**：https://github.com/hiwonder

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个功能包！

---

**作者**：ArmPi Team
**日期**：2026-03-22
**版本**：1.0.0
