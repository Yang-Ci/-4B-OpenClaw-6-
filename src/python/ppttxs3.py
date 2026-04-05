#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本转语音工具
使用 pyttsx3 库将文本转换为语音
"""

import os
import sys
import argparse
import pyttsx3


def print_usage():
    """打印使用说明"""
    print("=" * 60)
    print("          文本转语音工具 (ppttxs3)")
    print("=" * 60)
    print()
    print("用法:")
    print("  python ppttxs3.py [文本] [选项]")
    print("  python ppttxs3.py --file <文本文件> [选项]")
    print()
    print("参数:")
    print("  文本                  要转换的文本内容")
    print("  --file, -f            从文件读取文本")
    print("  --tts_output, -o          输出音频文件路径 (默认: ttx_output.wav)")
    print("  --rate, -r            语速 (默认: 150)")
    print("  --volume, -v          音量 (0.0-1.0, 默认: 1.0)")
    print("  --voice, -V           语音索引 (默认: 0，自动选择)")
    print("  --list-voices         列出所有可用的语音")
    print("  --help, -h            显示此帮助信息")
    print()
    print("示例:")
    print("  python ppttxs3.py '你好，这是一段测试文本'")
    print("  python ppttxs3.py --file text.txt -o output.mp3")
    print("  python ppttxs3.py '测试语速' --rate 200 --volume 0.8")
    print("  python ppttxs3.py --list-voices")
    print("=" * 60)


def list_voices():
    """列出所有可用的语音"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print("=" * 60)
        print("           可用语音列表")
        print("=" * 60)
        print(f"共找到 {len(voices)} 个语音:")
        print()
        
        for i, voice in enumerate(voices):
            print(f"  索引: {i}")
            print(f"  名称: {voice.name}")
            print(f"  ID: {voice.id}")
            print(f"  语言: {voice.languages}")
            print(f"  性别: {voice.gender}")
            print(f"  年龄: {voice.age}")
            print()
        
        print("提示: 使用 --voice 参数选择语音，例如 --voice 0")
        print("=" * 60)
        
    except Exception as e:
        print(f"获取语音列表失败: {e}")


def read_text_from_file(filepath):
    """从文件读取文本"""
    if not os.path.exists(filepath):
        print(f"错误: 找不到文件 '{filepath}'")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        if not text:
            print("错误: 文件内容为空")
            return None
        
        print(f"从文件读取文本，长度: {len(text)} 字符")
        print()
        return text
        
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None


def text_to_speech(text, output_file="ttx_output.wav", rate=150, volume=1.0, voice_index=0):
    """
    将文本转换为语音
    
    参数:
        text: 要转换的文本
        output_file: 输出音频文件路径
        rate: 语速
        volume: 音量 (0.0-1.0)
        voice_index: 语音索引
    
    返回:
        bool: 成功返回 True，失败返回 False
    """
    try:
        # 初始化引擎
        engine = pyttsx3.init()
        
        # 设置属性
        engine.setProperty('rate', rate)      # 语速
        engine.setProperty('volume', volume)  # 音量
        
        # 设置语音
        voices = engine.getProperty('voices')
        if 0 <= voice_index < len(voices):
            engine.setProperty('voice', voices[voice_index].id)
            print(f"使用语音: {voices[voice_index].name}")
        else:
            print("警告: 无效的语音索引，使用默认语音")
        
        print(f"语速: {rate}")
        print(f"音量: {volume}")
        print(f"输出文件: {output_file}")
        print()
        
        # 保存到文件
        print("正在转换文本为语音...")
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        
        print(f"\n转换完成! 音频已保存到: {output_file}")
        print(f"文件大小: {os.path.getsize(output_file) / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def main():
    """主函数"""
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="文本转语音工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python ppttxs3.py '你好，这是一段测试文本'
  python ppttxs3.py --file text.txt -o output.mp3
  python ppttxs3.py '测试语速' --rate 200 --volume 0.8
  python ppttxs3.py --list-voices
        """
    )
    
    parser.add_argument(
        "text",
        nargs="?",
        help="要转换的文本内容"
    )
    
    parser.add_argument(
        "--file", "-f",
        help="从文件读取文本"
    )
    
    parser.add_argument(
        "--tts_output", "-o",
        default="ttx_output.wav",
        help="输出音频文件路径 (默认: ttx_output.wav)"
    )
    
    parser.add_argument(
        "--rate", "-r",
        type=int,
        default=200,
        help="语速 (默认: 200)"
    )
    
    parser.add_argument(
        "--volume", "-v",
        type=float,
        default=1.0,
        help="音量 (0.0-1.0, 默认: 1.0)"
    )
    
    parser.add_argument(
        "--voice", "-V",
        type=int,
        default=0,
        help="语音索引 (默认: 0)"
    )
    
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="列出所有可用的语音"
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 列出语音
    if args.list_voices:
        list_voices()
        return 0
    
    # 获取文本
    text = None
    if args.file:
        text = read_text_from_file(args.file)
    elif args.text:
        text = args.text
    else:
        print("错误: 请提供文本内容或指定文本文件")
        print()
        print_usage()
        return 1
    
    if text is None:
        return 1
    
    # 检查音量范围
    if not 0.0 <= args.volume <= 1.0:
        print("错误: 音量必须在 0.0-1.0 之间")
        return 1
    
    # 执行转换
    success = text_to_speech(
        text,
        args.tts_output,
        args.rate,
        args.volume,
        args.voice
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    # 检查依赖
    try:
        import pyttsx3
    except ImportError:
        print("正在安装 pyttsx3 库...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "pyttsx3"])
        print("\n安装完成，请重新运行程序")
        sys.exit(1)
    
    sys.exit(main())
