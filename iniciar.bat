@echo off
chcp 65001 >nul
title Mundo Mágico do Teclado

echo ============================================================
echo   🌟 Mundo Mágico do Teclado - Brincadeira para Crianças 🌟
echo ============================================================
echo.
echo A verificar dependências...
python -c "import pygame" 2>nul
if %errorlevel% neq 0 (
    echo A instalar pygame-ce...
    python -m pip install pygame-ce
)

echo A iniciar em todos os monitores...
echo DICA: Para sair, mantenha a tecla ESC premida durante 2 segundos.
echo.

python main.py

exit

