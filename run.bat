@echo off
title WiFi Network Analyzer
cd /d "%~dp0"

echo ========================================================
echo               WiFi Network Analyzer
echo ========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment (.venv)...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python is installed and in PATH.
        pause
        exit /b 1
    )
    echo [2/3] Installing dependencies from requirements.txt...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    echo [OK] Virtual environment found.
)

echo.
echo [3/3] Launching WiFi Analyzer in Streamlit...
echo Opening browser at http://localhost:8501 ...
echo.
.\.venv\Scripts\python.exe -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo [Streamlit stopped]
    pause
)
