#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper 语音识别程序
使用 OpenAI Whisper 模型将音频转换为文本
"""

import os
import sys
import wave
import argparse
import warnings

# 忽略一些警告
warnings.filterwarnings("ignore")

# 设置 ffmpeg 路径（根据您的实际安装路径修改）
FFMPEG_PATH = r"C:\Users\Administrator\ffmpeg-2026-03-22-git-9c63742425-essentials_build\ffmpeg-2026-03-22-git-9c63742425-essentials_build\bin"
if os.path.exists(FFMPEG_PATH):
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ.get("PATH", "")


def print_usage():
    """打印使用说明"""
    print("=" * 50)
    print("       Whisper 语音识别程序")
    print("=" * 50)
    print()
    print("用法:")
    print("  python whisper_asr.py [音频文件路径] [选项]")
    print()
    print("参数:")
    print("  音频文件路径          要识别的音频文件（默认: output.wav）")
    print("  --model, -m          选择模型: tiny, base, small, medium, large")
    print("                       （默认: base）")
    print("  --language, -l       设置语言（默认: zh 中文）")
    print("  --output, -o         输出文本文件路径（可选）")
    print("  --list-models        列出所有可用模型")
    print()
    print("示例:")
    print("  python whisper_asr.py")
    print("  python whisper_asr.py output.wav")
    print("  python whisper_asr.py myaudio.wav --model small")
    print("  python whisper_asr.py audio.wav -m medium -l en")
    print("  python whisper_asr.py audio.wav -o result.txt")
    print("=" * 50)


def list_models():
    """列出可用的模型"""
    models = {
        "tiny": "~39 MB, 最快, 准确度较低",
        "base": "~74 MB, 快, 中等准确度（推荐）",
        "small": "~244 MB, 中等速度, 好准确度",
        "medium": "~769 MB, 较慢, 很好准确度",
        "large": "~1.5 GB, 最慢, 最好准确度",
        "large-v2": "~1.5 GB, large的改进版",
        "large-v3": "~1.5 GB, 最新版本"
    }
    print("=" * 50)
    print("           可用模型列表")
    print("=" * 50)
    for name, desc in models.items():
        print(f"  {name:12} - {desc}")
    print("=" * 50)


def check_wav_file(filepath):
    """检查WAV文件是否有效"""
    if not os.path.exists(filepath):
        print(f"错误: 找不到文件 '{filepath}'")
        return False
    
    try:
        with wave.open(filepath, 'rb') as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            n_frames = wf.getnframes()
            duration = n_frames / frame_rate
            
            print("音频文件信息:")
            print(f"  文件路径: {filepath}")
            print(f"  声道数: {channels}")
            print(f"  采样宽度: {sample_width * 8} bit")
            print(f"  采样率: {frame_rate} Hz")
            print(f"  总帧数: {n_frames}")
            print(f"  时长: {duration:.2f} 秒")
            print()
            return True
    except wave.Error as e:
        print(f"错误: 无效的WAV文件 - {e}")
        return False
    except Exception as e:
        print(f"错误: 无法读取文件 - {e}")
        return False


def transcribe_audio(audio_path, model_name="small", language="zh"):
    """
    使用OpenAI Whisper进行语音识别
    
    参数:
        audio_path: 音频文件路径
        model_name: 模型名称
        language: 语言代码
    
    返回:
        识别结果文本
    """
    try:
        import whisper
    except ImportError:
        print("错误: 未安装 whisper 库")
        print()
        print("请安装依赖:")
        print("  pip install openai-whisper")
        return None
    
    print(f"正在加载模型: {model_name}")
    print("首次使用时会自动下载模型文件...")
    print()
    
    try:
        # 加载模型
        model = whisper.load_model(model_name)
        
        print(f"正在进行语音识别...")
        print(f"语言: {language}")
        print()
        
        # 执行识别
        result = model.transcribe(
            audio_path,
            language=language,
            verbose=False  # 不显示详细进度
        )
        
        return result["text"]
        
    except FileNotFoundError as e:
        print(f"识别失败: {e}")
        print()
        print("提示: 这个错误通常是因为缺少 ffmpeg 可执行文件")
        print()
        print("详细解决方法:")
        print("1. 下载 ffmpeg:")
        print("   - 访问 https://ffmpeg.org/download.html")
        print("   - 选择 Windows 版本 (推荐: gyan.dev 或 BtbN 版本)")
        print("   - 下载后解压到一个固定位置，例如 C:\ffmpeg")
        print()
        print("2. 添加到系统 PATH:")
        print('   - 右键点击"此电脑" → "属性" → "高级系统设置" → "环境变量"')
        print('   - 在 "系统变量" 中找到 "Path"，点击 "编辑"')
        print('   - 点击 "新建"，添加 ffmpeg 的 bin 目录路径，例如 C:\\ffmpeg\\bin')
        print('   - 点击 "确定" 保存所有设置')
        print()
        print("3. 验证安装:")
        print("   - 打开新的命令提示符")
        print("   - 输入 'ffmpeg -version' 并按回车")
        print("   - 如果看到版本信息，说明安装成功")
        print()
        print("4. 重新运行本程序")
        return None
    except Exception as e:
        print(f"识别失败: {e}")
        return None


def main():
    """主函数"""
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="Whisper 语音识别工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python whisper_asr.py
  python whisper_asr.py output.wav
  python whisper_asr.py audio.wav --model small
  python whisper_asr.py audio.wav -m medium -l en -o result.txt
        """
    )
    
    parser.add_argument(
        "audio",
        nargs="?",
        default="output.wav",
        help="音频文件路径 (默认: output.wav)"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="small",
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help="选择模型 (默认: small)"
    )
    
    parser.add_argument(
        "--language", "-l",
        default="zh",
        help="设置语言代码 (默认: zh 中文)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="输出文本文件路径"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="列出所有可用模型"
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 列出模型
    if args.list_models:
        list_models()
        return 0
    
    # 检查音频文件
    if not check_wav_file(args.audio):
        return 1
    
    # 执行识别
    result = transcribe_audio(args.audio, args.model, args.language)
    
    if result is None:
        return 1
    
    # 显示结果
    print("=" * 50)
    print("           识别结果")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    # 保存到文件
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"\n结果已保存到: {args.output}")
        except Exception as e:
            print(f"\n保存文件失败: {e}")
    
    return 0


if __name__ == "__main__":
    # 检查是否安装了必要的依赖
    try:
        import whisper
    except ImportError:
        print("正在安装 whisper 库...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper"])
        print("\n安装完成，请重新运行程序")
        sys.exit(1)
    
    # 检查是否安装了 ffmpeg
    try:
        import ffmpeg
    except ImportError:
        print("正在安装 ffmpeg-python...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "ffmpeg-python"])
        print("\n安装完成，请重新运行程序")
        sys.exit(1)
    
    sys.exit(main())
