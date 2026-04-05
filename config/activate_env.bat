@echo off
echo ========================================
echo 激活 voice_assistant_env 环境...
echo ========================================
call conda activate voice_assistant_env
echo.
echo 环境已激活!
echo Python 版本:
python --version
echo.
echo ========================================
echo 已安装的依赖包:
echo ========================================
pip list | findstr "pyaudio whisper edge-tts dashscope fastmcp"
echo.
echo ========================================
echo 现在可以运行语音助手程序了
echo 例如：python voice_assistant_01.py
echo ========================================
