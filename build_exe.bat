@echo off
chcp 65001 >nul
title Compilar Executável - Mundo Mágico do Teclado

echo ============================================================
echo   A compilar TecladoMagico.exe (versão standalone sem instalação)
echo ============================================================
echo.

python -m PyInstaller --onefile --noconsole --clean --name "TecladoMagico" --icon="app_icon.ico" main.py

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo   SUCESSO! O ficheiro está pronto em: dist\TecladoMagico.exe
    echo ============================================================
) else (
    echo.
    echo [ERRO] Falha ao compilar o executável.
)
pause

