#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音助手程序（整合版）
功能：录音 → 语音识别 → 大模型回答 → 语音合成
整合了 Python 版本的录音功能
"""

import os
import sys
import time
import subprocess
import tempfile
import asyncio
import argparse
import wave
import warnings
import pyaudio
import threading
import re

# 忽略警告
warnings.filterwarnings("ignore")

# 设置 ffmpeg 路径（根据实际安装路径修改）
FFMPEG_PATH = r"C:\Users\Administrator\ffmpeg-2026-03-22-git-9c63742425-essentials_build\ffmpeg-2026-03-22-git-9c63742425-essentials_build\bin"
if os.path.exists(FFMPEG_PATH):
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ.get("PATH", "")


# ==================== 录音模块 ====================

# 音频参数
TARGET_SAMPLE_RATE = 16000
TARGET_CHANNELS = 1
BITS_PER_SAMPLE = 16
CHUNK = 1024


class AudioRecorder:
    """音频录音类"""
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


def record_audio(output_file="output.wav"):
    """
    录制音频（整合版本）
    直接在当前程序中录音，不需要启动外部程序
    """
    print("=" * 50)
    print("          开始录音")
    print("=" * 50)
    print("录音操作说明:")
    print("  - 按 R 键开始录音")
    print("  - 说话")
    print("  - 按 S 键停止录音并保存")
    print("=" * 50)
    
    import msvcrt
    
    recorder = AudioRecorder()
    
    if not recorder.initialize():
        print("音频设备初始化失败!")
        return False
    
    print("音频设备初始化成功!")
    print()
    
    try:
        while True:
            # 检查按键
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                print(f"{key.upper()}")
                
                if key == 'r':
                    if not recorder.is_recording:
                        recorder.start_recording()
                    else:
                        print("录音已经在进行中...")
                
                elif key == 's':
                    if recorder.is_recording:
                        recorder.stop_recording()
                        success = recorder.save_to_wav(output_file)
                        recorder.cleanup()
                        return success
                    else:
                        print("当前没有在录音")
                
                else:
                    print("无效命令，请输入 R 或 S")
            
            # 短暂等待
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n录音中断")
        if recorder.is_recording:
            recorder.stop_recording()
            recorder.save_to_wav(output_file)
        recorder.cleanup()
        return False
    except Exception as e:
        print(f"录音失败：{e}")
        recorder.cleanup()
        return False


# ==================== 语音识别模块 ====================

def transcribe_audio(audio_path, model_name="small", language="zh"):
    """
    使用 Whisper 进行语音识别
    """
    print("=" * 50)
    print("        语音识别中")
    print("=" * 50)
    
    try:
        import whisper
    except ImportError:
        print("正在安装 whisper 库...")
        subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper"])
        print("安装完成，重新运行程序")
        return None
    
    try:
        # 加载模型
        print(f"正在加载模型：{model_name}")
        model = whisper.load_model(model_name)
        
        # 执行识别
        print("正在识别音频...")
        result = model.transcribe(
            audio_path,
            language=language,
            verbose=False
        )
        
        text = result["text"].strip()
        if text:
            print(f"识别结果：{text}")
            return text
        else:
            print("识别失败：未识别到文本")
            return None
            
    except Exception as e:
        print(f"语音识别失败：{e}")
        return None


# ==================== 大模型调用模块 ====================

def call_llm(prompt, api_key="sk-8b65dfd067f44a629e8b8965fb2d285a"):
    """
    调用大模型
    """
    print("=" * 50)
    print("        大模型思考中")
    print("=" * 50)
    
    try:
        from dashscope import Generation
    except ImportError:
        print("正在安装 dashscope 库...")
        subprocess.run([sys.executable, "-m", "pip", "install", "dashscope"])
        print("安装完成，重新运行程序")
        return None
    
    try:
        print("正在调用大模型...")
        
        # 调用 Qwen 模型
        response = Generation.call(
            model='qwen-turbo',
            prompt=prompt,
            api_key=api_key
        )
        
        if response.status_code == 200:
            answer = response.output.text.strip()
            if answer:
                print(f"大模型回答：{answer}")
                return answer
            else:
                print("大模型返回空回答")
                return None
        else:
            print(f"大模型调用失败：{response.message}")
            return None
            
    except Exception as e:
        print(f"大模型调用失败：{e}")
        return None


# ==================== 文本清理模块 ====================

def clean_text_for_tts(text):
    """
    清理文本，过滤掉影响语音合成的特殊字符
    """
    # 移除 Markdown 格式符号
    import re
    
    # 移除星号（用于粗体/斜体）
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # *italic*
    
    # 移除井号（用于标题）
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    # 移除反引号（用于代码块）
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # 代码块
    text = re.sub(r'`([^`]+)`', r'\1', text)                # 行内代码
    
    # 移除方括号和链接
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url)
    
    # 移除多余的空行和空格
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()
    
    return text


# ==================== 语音合成模块 ====================

async def text_to_speech(text, output_file="response.wav", voice=None, language="mandarin"):
    """
    文本转语音
    """
    print("=" * 50)
    print("        语音合成中")
    print("=" * 50)
    
    # 清理文本，过滤特殊字符
    cleaned_text = clean_text_for_tts(text)
    print(f"原始文本长度：{len(text)}")
    print(f"清理后文本长度：{len(cleaned_text)}")
    print(f"清理后文本：{cleaned_text[:200]}...")
    
    try:
        import edge_tts
    except ImportError:
        print("正在安装 edge-tts 库...")
        subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts"])
        print("安装完成，重新运行程序")
        return False
    
    try:
        # 根据语言选择默认语音
        if not voice:
            if language == "cantonese":
                voice = "zh-HK-HiuMaanNeural"  # 粤语女声
            else:
                voice = "zh-CN-YunxiNeural"    # 普通话女声
        
        print(f"使用语音：{voice}")
        print("正在合成语音...")
        
        # 使用 edge_tts
        from edge_tts import Communicate
        tts = Communicate(cleaned_text, voice)
        
        # 保存到文件
        await tts.save(output_file)
        
        if os.path.exists(output_file):
            print(f"语音合成成功！文件已保存到：{output_file}")
            return True
        else:
            print("语音合成失败：未生成音频文件")
            return False
            
    except Exception as e:
        print(f"语音合成失败：{e}")
        return False


# ==================== 音频播放模块 ====================

def play_audio(audio_file):
    """
    播放音频
    """
    if not os.path.exists(audio_file):
        print(f"错误：找不到音频文件 {audio_file}")
        return False
    
    try:
        print("正在播放回答...")
        
        # 使用系统默认播放器
        if sys.platform == 'win32':
            os.startfile(audio_file)
        else:
            subprocess.run(['xdg-open', audio_file])
        
        return True
        
    except Exception as e:
        print(f"播放失败：{e}")
        return False


# ==================== 主函数 ====================

def main():
    """
    主函数
    """
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="语音助手程序（整合版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python voice_assistant_01.py
  python voice_assistant_01.py --language cantonese
  python voice_assistant_01.py --model medium
  python voice_assistant_01.py --language mandarin --model small
        """
    )
    
    parser.add_argument(
        "--language", "-l",
        default="mandarin",
        choices=["mandarin", "cantonese"],
        help="语言选择 (默认：mandarin)"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper 模型 (默认：small)"
    )
    
    parser.add_argument(
        "--tts-voice", "-v",
        help="TTS 语音名称"
    )
    
    # 解析参数
    args = parser.parse_args()
    
    print("=" * 70)
    print("            语音助手（整合版）")
    print("=" * 70)
    print(f"语言：{args.language}")
    print(f"Whisper 模型：{args.model}")
    print("=" * 70)
    print()
    
    # 1. 录音
    if not record_audio():
        print("录音失败，程序退出")
        return 1
    
    # 2. 语音识别
    language_code = "zh" if args.language == "mandarin" else "zh"
    text = transcribe_audio("output.wav", args.model, language_code)
    if not text:
        print("语音识别失败，程序退出")
        return 1
    
    # 3. 调用大模型
    prompt = f"请回答以下问题：{text}"
    answer = call_llm(prompt)
    if not answer:
        print("大模型调用失败，程序退出")
        return 1
    
    # 4. 语音合成
    output_file = f"response_{args.language}.wav"
    success = asyncio.run(text_to_speech(answer, output_file, args.tts_voice, args.language))
    if not success:
        print("语音合成失败，程序退出")
        return 1
    
    # 5. 播放音频
    play_audio(output_file)
    
    print("\n" + "=" * 70)
    print("            流程完成")
    print("=" * 70)
    print("录音文件：output.wav")
    print(f"回答音频：{output_file}")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    # 检查依赖
    try:
        import pyaudio
        import whisper
        import edge_tts
        from dashscope import Generation
    except ImportError:
        print("正在安装必要的依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", 
                       "pyaudio", "openai-whisper", "edge-tts", "dashscope"])
        print("\n依赖安装完成，请重新运行程序")
        sys.exit(1)
    
    sys.exit(main())
