#!/usr/bin/env python3
# 读取舵机状态的脚本

import sys
import os

# 添加路径以便导入armpi_pro模块
sys.path.append('/home/ubuntu/armpi_pro/src')

from armpi_pro import bus_servo_control
from ros_robot_controller_sdk import RobotController

class ServoReader:
    def __init__(self):
        self.board = RobotController()
        self.servo_control = bus_servo_control.BusServoControl(self.board)
    
    def read_position(self, servo_id):
        try:
            position = self.servo_control.getBusServoPulse(servo_id)
            if position is not None:
                return position
            else:
                return 500  # 默认值
        except Exception as e:
            print(f"Error reading servo {servo_id} position: {e}")
            return 500
    
    def read_temperature(self, servo_id):
        try:
            temp = self.servo_control.getBusServoTemp(servo_id)
            if temp is not None:
                return temp
            else:
                return 25  # 默认值
        except Exception as e:
            print(f"Error reading servo {servo_id} temperature: {e}")
            return 25
    
    def read_voltage(self, servo_id):
        try:
            voltage = self.servo_control.getBusServoVin(servo_id)
            if voltage is not None:
                return voltage
            else:
                return 6000  # 默认值
        except Exception as e:
            print(f"Error reading servo {servo_id} voltage: {e}")
            return 6000

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python read_servo_state.py <servo_id>")
        sys.exit(1)
    
    servo_id = int(sys.argv[1])
    reader = ServoReader()
    
    position = reader.read_position(servo_id)
    temperature = reader.read_temperature(servo_id)
    voltage = reader.read_voltage(servo_id)
    
    print(f"{position},{temperature},{voltage}")
