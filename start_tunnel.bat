@echo off
title AutoVision.AI Tunnel Launcher
echo.
echo ===========================================
echo   Khoi dong Cloudflare Tunnel cho AI Web
echo ===========================================
echo.

:: Kiem tra cloudflared da cai dat chua
where cloudflared >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Khong tim thay cloudflared! 
    echo Vui long chay: winget install Cloudflare.cloudflared
    pause
    exit /b
)

echo Dang kich hoat tunnel cho http://localhost:7860...
echo Vui long doi lay link public (ket thuc bang .trycloudflare.com)
echo.

cloudflared tunnel --url http://localhost:7860

pause
