#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge TTS 文本转语音工具
使用 Microsoft Edge TTS 服务将文本转换为语音
"""

import os
import sys
import argparse
import asyncio


def print_usage():
    """打印使用说明"""
    print("=" * 60)
    print("        Edge TTS 文本转语音工具")
    print("=" * 60)
    print()
    print("用法:")
    print("  python edge_tts_tool.py [文本] [选项]")
    print("  python edge_tts_tool.py --file <文本文件> [选项]")
    print()
    print("参数:")
    print("  文本                  要转换的文本内容")
    print("  --file, -f            从文件读取文本")
    print("  --output, -o          输出音频文件路径 (默认: edge_output.wav)")
    print("  --voice, -v           语音名称 (默认: zh-CN-YunxiNeural)")
    print("  --rate, -r            语速 (默认: +0%)")
    print("  --volume, -V          音量 (默认: +0%)")
    print("  --list-voices         列出所有可用的语音")
    print("  --help, -h            显示此帮助信息")
    print()
    print("推荐语音:")
    print("  普通话: zh-CN-YunxiNeural (女声), zh-CN-YunyangNeural (男声)")
    print("  粤语: zh-HK-HiuMaanNeural (女声), zh-HK-WanLungNeural (男声)")
    print("  英语: en-US-AriaNeural (女声), en-US-ChristopherNeural (男声)")
    print()
    print("示例:")
    print("  python edge_tts_tool.py '你好，这是一段测试文本'")
    print("  python edge_tts_tool.py '你好，呢个系一段测试文本' --voice zh-HK-HiuMaanNeural")
    print("  python edge_tts_tool.py --file text.txt -o output.mp3")
    print("  python edge_tts_tool.py '测试语速' --rate '+20%' --volume '-10%'")
    print("  python edge_tts_tool.py --list-voices")
    print("=" * 60)


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


async def list_available_voices():
    """列出所有可用的语音"""
    try:
        import edge_tts
        
        print("正在获取可用语音列表...")
        from edge_tts import list_voices
        voices = await list_voices()
        
        print("=" * 60)
        print("           可用语音列表")
        print("=" * 60)
        print(f"共找到 {len(voices)} 个语音:")
        print()
        
        # 按语言分组
        voices_by_language = {}
        for voice in voices:
            language = voice['Locale']
            if language not in voices_by_language:
                voices_by_language[language] = []
            voices_by_language[language].append(voice)
        
        # 显示语音
        for language, lang_voices in voices_by_language.items():
            print(f"  语言: {language}")
            for voice in lang_voices:
                name = voice['ShortName']
                gender = voice['Gender']
                print(f"    - {name} ({gender})")
            print()
        
        print("提示: 使用 --voice 参数选择语音，例如 --voice zh-CN-YunxiNeural")
        print("=" * 60)
        
    except Exception as e:
        print(f"获取语音列表失败: {e}")


async def text_to_speech(text, output_file="edge_output.wav", voice="zh-CN-YunxiNeural", rate="+0%", volume="+0%"):
    """
    将文本转换为语音
    
    参数:
        text: 要转换的文本
        output_file: 输出音频文件路径
        voice: 语音名称
        rate: 语速
        volume: 音量
    
    返回:
        bool: 成功返回 True，失败返回 False
    """
    try:
        import edge_tts
        
        print(f"使用语音: {voice}")
        print(f"语速: {rate}")
        print(f"音量: {volume}")
        print(f"输出文件: {output_file}")
        print()
        
        print("正在转换文本为语音...")
        print("这可能需要几秒钟时间，请耐心等待...")
        
        # 使用 edge_tts 的新 API
        from edge_tts import Communicate
        tts = Communicate(text, voice, rate=rate, volume=volume)
        
        # 保存到文件
        await tts.save(output_file)
        
        print(f"\n转换完成! 音频已保存到: {output_file}")
        if os.path.exists(output_file):
            print(f"文件大小: {os.path.getsize(output_file) / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def main():
    """主函数"""
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="Edge TTS 文本转语音工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python edge_tts_tool.py '你好，这是一段测试文本'
  python edge_tts_tool.py '你好，呢个系一段测试文本' --voice zh-HK-HiuMaanNeural
  python edge_tts_tool.py --file text.txt -o output.mp3
  python edge_tts_tool.py '测试语速' --rate '+20%' --volume '-10%'
  python edge_tts_tool.py --list-voices
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
        "--output", "-o",
        default="edge_output.wav",
        help="输出音频文件路径 (默认: edge_output.wav)"
    )
    
    parser.add_argument(
        "--voice", "-v",
        default="zh-CN-YunxiNeural",
        help="语音名称 (默认: zh-CN-YunxiNeural)"
    )
    
    parser.add_argument(
        "--rate", "-r",
        default="+0%",
        help="语速 (默认: +0%)"
    )
    
    parser.add_argument(
        "--volume", "-V",
        default="+0%",
        help="音量 (默认: +0%)"
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
        asyncio.run(list_available_voices())
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
    
    # 执行转换
    success = asyncio.run(text_to_speech(
        text,
        args.output,
        args.voice,
        args.rate,
        args.volume
    ))
    
    return 0 if success else 1


if __name__ == "__main__":
    # 检查依赖
    try:
        import edge_tts
    except ImportError:
        print("正在安装 edge-tts 库...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts"])
        print("\n安装完成，请重新运行程序")
        sys.exit(1)
    
    sys.exit(main())
