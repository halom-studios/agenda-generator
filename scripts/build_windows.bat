@echo off
setlocal
echo ====================================================
echo  Compilador do Gerador de Agenda para Windows (.exe)
echo ====================================================

:: Garante que esta na raiz do projeto (um nivel acima da pasta scripts)
cd /d "%~dp0\.."

echo [1/3] Verificando Python...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERRO: Python nao encontrado no PATH do Windows.
    echo Por favor, instale o Python 3.10 ou superior marcando a opcao "Add Python to PATH".
    pause
    exit /b 1
)

echo [2/3] Configurando ambiente virtual e dependencias...
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo [3/3] Compilando executavel standalone (.exe)...
flet pack --name "GeradorAgenda" --hidden-import odfdo --onedir -y scripts\gui_agenda.py

echo.
echo ====================================================
echo  Sucesso! Executavel gerado em:
echo  dist\GeradorAgenda\GeradorAgenda.exe
echo ====================================================
pause
