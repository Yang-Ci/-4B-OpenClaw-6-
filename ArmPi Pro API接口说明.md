# ArmPi Pro API

## armpi_pro_common

### 映射（主要用于舵机角度与舵机脉宽的映射）
from armpi_pro import misc
misc.map(x, in_min, in_max, out_min, out_max)
函数的参数：
x：要映射的值
in_min：输入范围的最小值
in_max：输入范围的最大值
out_min：输出范围的最小值
out_max：输出范围的最大值

### 设置范围的函数（主要用于舵机角度范围的限制）
misc.setRange(x, x_min, x_max)
函数的参数：
x：要设置范围的值
x_min：范围的最小值
x_max：范围的最大值

### pid控制
from armpi_pro import pid

#### 初始化pid
pid.PID()
初始化PID对象，会设置初始的P、I、D三个参数。
分别设置成P = 0.2 、I = 0 、D = 0。
也可以自行设置P、I、D三个参数，具体方法如下：
pid.PID(P=0.1,I=0.0001,D=0.000006)

#### 设置PID控制目标值
pid.PID.SetPoint = target_value
参数
target_value(数值类型) – 目标值

#### 清除PID计算参数和PID系数
pid.PID.clear()

#### 更新PID当前值
pid.PID.update(current_value)
参数
current_value(数值类型) – 当前值

#### 获得PID运算结果
pid.PID.output
返回类型：数值类型

### 舵机控制
from armpi_pro import bus_servo_control

#### 设置舵机角度、运行时间
bus_servo_control.set_servos(pub, duration, pos_s)
函数的参数：
pub：舵机控制的话题名称
duration（int）：运行时间，单位为毫秒
pos_s(turple)：设置舵机的ID号与转动的脉宽

```
joints_pub = rospy.Publisher('/servo_controllers/port_id_1/multi_id_pos_dur', MultiRawIdPosDur, queue_size=1)
bus_servo_control.set_servosset_servos(joints_pub, 1000, ((6, 350), (1, 200)))
```

### 机械臂逆运动学控制
from kinematics import ik_transform

#### 设置机械臂坐标、俯仰角及范围
ik_transform.ArmIK().setPitchRanges(coordinate_data, alpha, alpha1, alpha2)
函数的参数：
coordinate_data：给定坐标（X,Y,Z），单位为米
alpha：机械臂俯仰角
alpha1：机械臂俯仰角的范围
alpha2：机械臂俯仰角的范围
返回类型：数组
返回说明：
({'theta3': angle3, 'theta4': angle4, 'theta5':angle5, 'theta6': angle6}, {'servo3': pulse3, 'servo4': pulse4, 'servo5': pulse5, 'servo6': pulse6}, alpha)
第一个参数为字典类型，表示各个关节的角度，
第二个参数为字典类型，表示各个舵机的脉宽，
第三个参数为数值类型，表示机械臂的俯仰角。

```
target = ik_transform.ArmIK().setPitchRanges((0, 0.15, 0.0), -180, -180, 0) # 逆运动学求解
joints_pub = rospy.Publisher('/servo_controllers/port_id_1/multi_id_pos_dur', MultiRawIdPosDur, queue_size=1)
servo_data = target[1]
bus_servo_control.set_servos(joints_pub, 1000, ((1, 450), (2, 500), (3, servo_data['servo3']), (4, servo_data['servo4']), (5, servo_data['servo5']), (6, servo_data['servo6'])))
```

### 麦轮底盘运动控制
#### 控制小车移动方向、线速度、偏航角速度
set_velocity.publish(velocity, direction, angular_rate)
函数的参数：
velocity：线速度
direction：方向角（以ArmPi Pro为第一视角，90为正前方，270为正后方，180为正左边，0为正右边）
angular_rate:偏航角速度（正数：为逆时针，即右旋转；负数：为顺时针，即左旋转；）

```
set_velocity = rospy.Publisher('/chassis_control/set_velocity', SetVelocity, queue_size=1)
set_velocity.publish(60,90,0) # 以速度60向前移动
```

#### 控制小车平移
translation.publish(velocity_x, velocity_y)
函数的参数：
velocity_x：X方向上的线速度（以ArmPi Pro为第一视角，X方向为正前后方）
velocity_y：Y方向上的线速度（以ArmPi Pro为第一视角，Y方向为正左右边）

```
translation = rospy.Publisher('/chassis_control/set_translation', SetTranslation, queue_size=1)
translation.publish(60，0) # 以速度60向前移动
```

### 硬件驱动
#### 控制LED灯
led_pub.publish(id, on_time, off_time, repeat)
函数的参数：
id：LED灯的ID号
on_time:起始时间
off_time:结束时间
repeat:频率

```
led_pub = rospy.Publisher('/ros_robot_controller/set_led', LedState, queue_size=1)
led_pub.publish(1，0.1, 0.9, 1) # LED1以0.8秒的时间闪烁一次
```

#### 控制蜂鸣器
buzzer_pub.publish(freq, on_time, off_time, repeat)
函数的参数：
freq：LED灯的ID号
on_time:起始时间
off_time:结束时间
repeat:频率

```
buzzer_pub = rospy.Publisher('/ros_robot_controller/set_buzzer', BuzzerState, queue_size=1)
buzzer_pub.publish(1900, 0.1, 0.9, 1)# 蜂鸣器以1900的频率响0.8秒，次数为1
```

#### 控制OELD屏幕
oled_pub.publish(index, text)
函数的参数：
index：索引号
text:需要显示的文本


```
oled_pub = rospy.Publisher('/ros_robot_controller/set_oled', OLEDState, queue_size=1)
oled_pub.publish(0, "hiwonder")# 在第1行显示“hiwonder”
```

#### 控制电机
motors_pub.publish(ros_robot_controller/MotorState[id,rps] data)
函数的参数：
id：电机ID号
rps:速度

```
motors_pub = rospy.Publisher('/ros_robot_controller/set_motor', MotorsState, queue_size=1)
motors_pub.publish([[1,20],[2,20]])# 设置电机ID1和2速度为20
```

#### 控制RGB灯
rgb_pub.publish(ros_robot_controller/RGBState[id, r, g, b] data)
函数的参数：
id：RGB灯ID号
r:颜色的red通道
g:颜色的green通道
b:颜色的bule通道

```
rgb_pub = rospy.Publisher('/ros_robot_controller/set_rgb', RGBsState, queue_size=1)
rgb_pub.publish([[1, 0, 0, 255],[2, 0, 0, 255]])# 设置RGB灯1和2颜色为红色
```

#### 控制总线舵机
bus_pub.publish(ros_robot_controller/BusServoState[present_id, target_id, position, offset, voltage, temperature, position_limit, voltage_limit, max_temperature_limit, enable_torque, save_offset, stop] state)
函数的参数：
present_id: 当前舵机的ID
target_id: 设置舵机的ID
position:舵机位置
offset: 舵机的偏差
voltage: 舵机的电压
temperature: 舵机的温度
position_limit: 舵机的位置限制
voltage_limit: 舵机的电压限制
max_temperature_limit: 舵机的温度限制
enable_torque: 舵机的力矩状态。 1：表示开启， 0：表示关闭
save_offset: 舵机偏差的保存状态。 1：表示保存成功， 0：表示保存失败
stop: 舵机的停止状态

#### 控制PWM舵机
pwm_pub.publish(ros_robot_controller/PWMServoState[id, position, offset] state)
函数的参数：
id: 舵机的ID
position:舵机位置
offset: 舵机偏差























