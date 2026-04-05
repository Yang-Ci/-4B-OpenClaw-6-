#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频录音程序（Python 版本）
功能：录制音频并保存为 WAV 文件（16kHz，单声道，16 位）
"""

import pyaudio
import wave
import threading
import time
import sys
import msvcrt

# 音频参数
TARGET_SAMPLE_RATE = 16000
TARGET_CHANNELS = 1
BITS_PER_SAMPLE = 16
CHUNK = 1024


class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.should_stop = False
        self.audio_data = []
        self.record_thread = None
        self.audio = None
        self.stream = None
        
    def initialize(self):
        """初始化音频设备"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # 获取默认输入设备信息
            default_device = self.audio.get_default_input_device_info()
            print(f"使用设备：{default_device['name']}")
            
            return True
        except Exception as e:
            print(f"初始化失败：{e}")
            return False
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            print("录音已经在进行中...")
            return
        
        self.audio_data = []
        self.should_stop = False
        self.is_recording = True
        
        try:
            # 打开音频流
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=TARGET_CHANNELS,
                rate=TARGET_SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            # 启动录音线程
            self.record_thread = threading.Thread(target=self._record_loop)
            self.record_thread.start()
            
            print(">>> 正在录音中... (按 S 停止录音)")
            
        except Exception as e:
            print(f"开始录音失败：{e}")
            self.is_recording = False
    
    def _record_loop(self):
        """录音循环"""
        while not self.should_stop:
            try:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                self.audio_data.append(data)
            except Exception as e:
                print(f"录音错误：{e}")
                break
    
    def stop_recording(self):
        """停止录音"""
        if not self.is_recording:
            print("当前没有在录音")
            return
        
        self.should_stop = True
        
        # 等待录音线程结束
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join()
        
        # 关闭流
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        self.is_recording = False
        print("录音已停止")
    
    def save_to_wav(self, filename):
        """保存为 WAV 文件"""
        if not self.audio_data:
            print("没有录音数据可保存")
            return False
        
        try:
            # 合并所有音频数据
            audio_bytes = b''.join(self.audio_data)
            
            # 创建 WAV 文件
            wf = wave.open(filename, 'wb')
            wf.setnchannels(TARGET_CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(TARGET_SAMPLE_RATE)
            wf.writeframes(audio_bytes)
            wf.close()
            
            print(f"录音已保存到：{filename}")
            print(f"录音时长：{len(self.audio_data) * CHUNK / TARGET_SAMPLE_RATE:.2f} 秒")
            print(f"数据大小：{len(audio_bytes)} 字节")
            
            return True
            
        except Exception as e:
            print(f"保存失败：{e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        if self.stream:
            self.stream.close()
        if self.audio:
            self.audio.terminate()


def check_for_key_press():
    """检查按键输入"""
    if msvcrt.kbhit():
        key = msvcrt.getch()
        return key.decode('utf-8').lower()
    return None


def main():
    """主函数"""
    print("=" * 50)
    print("        音频录音程序（Python 版本）")
    print("=" * 50)
    print()
    print("提示：按 R 键开始录音，按 S 键停止录音并保存，然后自动退出")
    print("=" * 50)
    print()
    
    recorder = AudioRecorder()
    
    if not recorder.initialize():
        print("音频设备初始化失败!")
        print("请按任意键退出...")
        input()
        return 1
    
    print("音频设备初始化成功!")
    print()
    
    try:
        while True:
            # 检查按键
            key = check_for_key_press()
            
            if key:
                print(f"{key.upper()}")
                
                if key == 'r':
                    if not recorder.is_recording:
                        recorder.start_recording()
                    else:
                        print("录音已经在进行中...")
                
                elif key == 's':
                    if recorder.is_recording:
                        recorder.stop_recording()
                        recorder.save_to_wav("output.wav")
                        print("程序即将退出...")
                        return 0
                    else:
                        print("当前没有在录音")
                
                else:
                    print("无效命令，请输入 R 或 S")
            
            # 短暂等待
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n程序中断")
    finally:
        if recorder.is_recording:
            recorder.stop_recording()
            recorder.save_to_wav("output.wav")
        recorder.cleanup()
    
    return 0


if __name__ == "__main__":
    # 检查依赖
    try:
        import pyaudio
    except ImportError:
        print("正在安装 pyaudio 库...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "pyaudio"])
        print("\n依赖安装完成，请重新运行程序")
        sys.exit(1)
    
    sys.exit(main())
