@echo off
chcp 65001 >nul
echo ========================================
echo   ArmPi Pro Simulator - 安装依赖
echo ========================================
echo.
echo [1/2] 检查 Node.js 环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js！
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
echo Node.js 版本:
node --version
echo.

echo [2/2] 安装项目依赖...
call npm install
if %errorlevel% neq 0 (
    echo.
    echo [错误] 依赖安装失败，请检查网络连接！
    pause
    exit /b 1
)

echo.
echo ========================================
echo   依赖安装完成！
echo ========================================
echo.
pause
