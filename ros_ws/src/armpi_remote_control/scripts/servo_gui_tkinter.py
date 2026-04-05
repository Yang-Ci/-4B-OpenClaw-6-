#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArmPi Servo Control GUI using Tkinter
简单的图形化舵机控制界面
"""

import rospy
from armpi_remote_control.msg import ServoControl, ServoStateFull
import tkinter as tk
from tkinter import ttk
import threading

class ServoGUI:
    def __init__(self):
        # 初始化ROS节点
        rospy.init_node('servo_gui_tkinter', anonymous=True)
        
        # 发布器
        self.servo_control_pub = rospy.Publisher('/armpi_remote/servo_control', 
                                                  ServoControl, queue_size=10)
        
        # 订阅器
        self.servo_state_sub = rospy.Subscriber('/armpi_remote/servo_states', 
                                                 ServoStateFull, self.servo_state_callback)
        
        # 存储当前位置
        self.current_positions = {i: 500 for i in range(1, 7)}
        # 存储滑块位置（用户设置的目标位置）
        self.slider_positions = {i: 500 for i in range(1, 7)}
        # 是否正在调节滑块
        self.adjusting_slider = False
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("ArmPi Servo Control")
        self.root.geometry("600x500")
        
        # 创建界面
        self.create_widgets()
        
        # 启动ROS spin线程
        self.ros_thread = threading.Thread(target=self.ros_spin)
        self.ros_thread.daemon = True
        self.ros_thread.start()
        
    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="ArmPi Servo Control", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 舵机控制框架
        control_frame = tk.LabelFrame(self.root, text="Servo Control", 
                                      font=("Arial", 12))
        control_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # 舵机滑块
        self.sliders = {}
        self.position_labels = {}
        
        for i in range(1, 7):
            row = tk.Frame(control_frame)
            row.pack(fill="x", padx=10, pady=5)
            
            # 标签
            label = tk.Label(row, text=f"Servo {i}:", width=10)
            label.pack(side="left")
            
            # 滑块
            slider = tk.Scale(row, from_=0, to=1000, orient=tk.HORIZONTAL, 
                             length=300, command=lambda val, idx=i: self.update_position_label(idx, val))
            slider.set(500)
            # 添加滑块事件处理
            slider.bind('<ButtonPress-1>', lambda e, idx=i: self.start_slider_adjust(idx))
            slider.bind('<ButtonRelease-1>', lambda e, idx=i: self.stop_slider_adjust(idx))
            slider.pack(side="left", padx=10)
            self.sliders[i] = slider
            
            # 位置显示
            pos_label = tk.Label(row, text="500", width=5)
            pos_label.pack(side="left")
            self.position_labels[i] = pos_label
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # 设置位置按钮
        set_btn = tk.Button(button_frame, text="Set Position", 
                           command=self.set_positions, 
                           font=("Arial", 12), width=15, height=2)
        set_btn.pack(side="left", padx=10)
        
        # 回家按钮
        home_btn = tk.Button(button_frame, text="Home Position", 
                            command=self.go_home, 
                            font=("Arial", 12), width=15, height=2)
        home_btn.pack(side="left", padx=10)
        
        # 停止按钮
        stop_btn = tk.Button(button_frame, text="Stop All", 
                            command=self.stop_all, 
                            font=("Arial", 12), width=15, height=2, bg="red")
        stop_btn.pack(side="left", padx=10)
        
        # 状态栏
        self.status_label = tk.Label(self.root, text="Ready", 
                                     bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side="bottom", fill="x")
        
    def start_slider_adjust(self, servo_id):
        # 开始调节滑块
        self.adjusting_slider = True
    
    def stop_slider_adjust(self, servo_id):
        # 停止调节滑块，保存当前滑块位置
        self.adjusting_slider = False
        self.slider_positions[servo_id] = self.sliders[servo_id].get()
    
    def update_position_label(self, servo_id, value):
        # 更新位置显示
        self.position_labels[servo_id].config(text=str(int(float(value))))
        # 保存滑块位置
        self.slider_positions[servo_id] = int(float(value))
        
    def set_positions(self):
        msg = ServoControl()
        msg.header.stamp = rospy.Time.now()
        
        # 正确初始化数组字段
        msg.servo_ids = []
        msg.positions = []
        msg.durations = []
        
        for i in range(1, 7):
            msg.servo_ids.append(i)
            msg.positions.append(self.slider_positions[i])
            msg.durations.append(500)  # 500ms
        
        msg.save_deviation = False
        self.servo_control_pub.publish(msg)
        self.status_label.config(text="Position set sent")
        
    def go_home(self):
        msg = ServoControl()
        msg.header.stamp = rospy.Time.now()
        
        # 正确初始化数组字段
        msg.servo_ids = []
        msg.positions = []
        msg.durations = []
        
        for i in range(1, 7):
            msg.servo_ids.append(i)
            msg.positions.append(500)
            msg.durations.append(1000)  # 1s
            self.sliders[i].set(500)
            self.position_labels[i].config(text="500")
            self.slider_positions[i] = 500
        
        msg.save_deviation = False
        self.servo_control_pub.publish(msg)
        self.status_label.config(text="Going to home position")
        
    def stop_all(self):
        msg = ServoControl()
        msg.header.stamp = rospy.Time.now()
        msg.save_deviation = False
        self.servo_control_pub.publish(msg)
        self.status_label.config(text="All servos stopped")
        
    def servo_state_callback(self, msg):
        # 在GUI线程中更新
        self.root.after(0, self.update_servo_state, msg)
        
    def update_servo_state(self, msg):
        servo_id = msg.servo_id
        if 1 <= servo_id <= 6:
            # 只有在用户没有调节滑块时才更新滑块位置
            if not self.adjusting_slider:
                # 只更新显示，不更新滑块位置
                self.position_labels[servo_id].config(text=str(msg.position))
            # 保存当前位置
            self.current_positions[servo_id] = msg.position
            
    def ros_spin(self):
        rospy.spin()
        
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    try:
        gui = ServoGUI()
        gui.run()
    except rospy.ROSInterruptException:
        pass
