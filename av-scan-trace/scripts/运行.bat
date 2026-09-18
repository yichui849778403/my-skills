@echo off
title AntiVirus Scan Recorder
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scan-record.ps1"
echo.
pause
