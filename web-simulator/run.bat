@echo off
chcp 65001 >nul
echo ========================================
echo   ArmPi Pro Simulator - 启动服务器
echo ========================================
echo.

echo [1/2] 检查依赖是否已安装...
if not exist "node_modules" (
    echo [提示] 未检测到 node_modules，正在安装依赖...
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败！
        pause
        exit /b 1
    )
)

echo [2/2] 启动服务器...
echo.
start http://localhost:3000
node server.js

pause
