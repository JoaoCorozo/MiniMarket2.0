@echo off
chcp 65001 >nul
title Minimarket Pily — Sistema POS

echo.
echo  ╔══════════════════════════════════════╗
echo  ║   🍄 MINIMARKET PILY — Sistema POS   ║
echo  ╚══════════════════════════════════════╝
echo.

:: Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python no está instalado.
    echo.
    echo  Por favor instalá Python desde:
    echo  https://www.python.org/downloads/
    echo.
    echo  Asegurate de marcar "Add Python to PATH"
    echo  durante la instalación.
    echo.
    pause
    exit /b 1
)

:: Verificar que los archivos necesarios existen
if not exist "%~dp0servidor.py" (
    echo  [ERROR] No se encontró servidor.py
    echo  Asegurate de que todos los archivos estén en la misma carpeta.
    pause
    exit /b 1
)

if not exist "%~dp0Minimarket_Pily.html" (
    echo  [ERROR] No se encontró Minimarket_Pily.html
    echo  Asegurate de que todos los archivos estén en la misma carpeta.
    pause
    exit /b 1
)

echo  ✓ Python encontrado
echo  ✓ Archivos verificados
echo.
echo  Iniciando sistema...
echo  El navegador se abrirá automáticamente.
echo.
echo  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  IMPORTANTE: No cierres esta ventana
echo  mientras estés usando el sistema.
echo  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: Cambiar al directorio del bat (para que datos.json se guarde ahí)
cd /d "%~dp0"

:: Ejecutar el servidor
python servidor.py

echo.
echo  Sistema cerrado. Hasta luego.
pause
