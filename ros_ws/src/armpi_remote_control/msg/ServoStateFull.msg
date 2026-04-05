# ServoStateFull.msg - 完整舵机状态消息
# 用于发布舵机的所有状态信息

Header header

# 舵机ID
uint8 servo_id

# 当前位置 (0-1000)
uint16 position

# 偏差值 (-125~125)
int16 deviation

# 温度 (摄氏度)
uint8 temperature

# 电压 (毫伏)
uint16 voltage

# 温度限制
uint8 temp_limit

# 角度限制 (最小, 最大)
uint16 angle_limit_min
uint16 angle_limit_max

# 电压限制 (最小, 最大)
uint16 voltage_limit_min
uint16 voltage_limit_max

# 扭矩状态 (0: 掉电, 1: 上电)
uint8 torque_state
