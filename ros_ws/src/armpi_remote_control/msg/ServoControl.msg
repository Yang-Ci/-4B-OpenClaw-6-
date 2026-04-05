# ServoControl.msg - 舵机控制消息
# 用于远程控制单个或多个舵机

Header header

# 舵机ID列表
uint8[] servo_ids

# 目标位置列表 (0-1000)
uint16[] positions

# 运行时间列表 (毫秒)
uint16[] durations

# 是否保存偏差
bool save_deviation
