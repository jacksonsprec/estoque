@echo off
cd /d "%~dp0"
py app.py
if errorlevel 1 (
    echo.
    echo O programa falhou ao iniciar.
    echo Verifique se o Python esta instalado e se as dependencias do projeto estao presentes.
    pause
)
