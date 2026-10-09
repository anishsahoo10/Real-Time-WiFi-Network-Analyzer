# WiFi Network Analyzer PowerShell Launcher
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "              WiFi Network Analyzer                    " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "[1/3] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "[2/3] Installing dependencies..." -ForegroundColor Yellow
    .\.venv\Scripts\pip install -r requirements.txt
} else {
    Write-Host "[OK] Virtual environment detected." -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/3] Launching WiFi Analyzer Dashboard..." -ForegroundColor Green
Write-Host "Opening browser at http://localhost:8501 ..." -ForegroundColor Cyan
Write-Host ""

& .\.venv\Scripts\python.exe -m streamlit run app.py
