@echo off
python --version >nul 2>&1
if errorlevel 1 (
    echo Python ist nicht installiert. Bitte installiere Python und versuche es erneut.
    exit /b
)

virtualenv --version >nul 2>&1
if errorlevel 1 (
    echo virtualenv ist nicht installiert. Bitte installiere virtualenv und versuche es erneut.
    exit /b
)

cd ..
python -m venv .\venv
