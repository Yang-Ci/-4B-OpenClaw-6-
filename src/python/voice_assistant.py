#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音助手程序
功能：录音 → 语音识别 → 大模型回答 → 语音合成
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

# 忽略警告
warnings.filterwarnings("ignore")

# 设置 ffmpeg 路径（根据实际安装路径修改）
FFMPEG_PATH = r"C:\Users\Administrator\ffmpeg-2026-03-22-git-9c63742425-essentials_build\ffmpeg-2026-03-22-git-9c63742425-essentials_build\bin"
if os.path.exists(FFMPEG_PATH):
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ.get("PATH", "")


def print_usage():
    """打印使用说明"""
    print("=" * 70)
    print("            语音助手程序")
    print("=" * 70)
    print()
    print("用法:")
    print("  python voice_assistant.py [选项]")
    print()
    print("参数:")
    print("  --language, -l        语言选择：mandarin (普通话), cantonese (粤语)")
    print("                        (默认：mandarin)")
    print("  --model, -m           Whisper 模型：tiny, base, small, medium, large")
    print("                        (默认：small)")
    print("  --tts-voice, -v       TTS 语音名称")
    print("  --help, -h            显示此帮助信息")
    print()
    print("示例:")
    print("  python voice_assistant.py")
    print("  python voice_assistant.py --language cantonese")
    print("  python voice_assistant.py --model medium")
    print("  python voice_assistant.py --language mandarin --model small")
    print("=" * 70)


def record_audio(output_file="output.wav"):
    """
    录制音频
    使用 audio_receive.exe 进行录音
    """
    print("=" * 50)
    print("          开始录音")
    print("=" * 50)
    print("录音操作说明:")
    print("  - 按 R 键开始录音")
    print("  - 说话")
    print("  - 按 S 键停止录音并保存")
    print("  - 按 Q 键退出程序")
    print("=" * 50)
    
    # 检查 audio_receive.exe 是否存在
    exe_path = os.path.join(os.getcwd(), "audio_receive.exe")
    
    if not os.path.exists(exe_path):
        print("错误：找不到 audio_receive.exe")
        print("请先编译 audio_receive.cpp:")
        print("  g++ audio_receive.cpp -o audio_receive.exe -lole32 -luuid -lwinmm -lksuser -std=c++11")
        return False
    
    try:
        # 启动录音程序
        print(f"\n正在启动录音程序...")
        print("录音程序窗口已打开，请在其中操作")
        print("=" * 50)
        
        # 使用 subprocess 启动录音程序，等待其退出
        result = subprocess.run([exe_path], capture_output=False)
        
        # 检查录音文件是否生成
        if os.path.exists(output_file):
            print(f"\n录音成功！文件已保存到：{output_file}")
            return True
        else:
            print("\n录音失败：未生成录音文件")
            print("请确保在录音程序中按了 S 键停止录音")
            return False
            
    except Exception as e:
        print(f"录音失败：{e}")
        return False


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


def main():
    """
    主函数
    """
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="语音助手程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python voice_assistant.py
  python voice_assistant.py --language cantonese
  python voice_assistant.py --model medium
  python voice_assistant.py --language mandarin --model small
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
    print("            语音助手")
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
        import whisper
        import edge_tts
        from dashscope import Generation
    except ImportError:
        print("正在安装必要的依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper", "edge-tts", "dashscope"])
        print("\n依赖安装完成，请重新运行程序")
        sys.exit(1)
    
    sys.exit(main())
