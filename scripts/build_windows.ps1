# Compilador do Gerador de Agenda para Windows (.exe)
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

Write-Host "==> [1/3] Verificando instalacao do Python..." -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python não encontrado. Instale o Python >= 3.10 com 'Add Python to PATH'."
    exit 1
}

Write-Host "==> [2/3] Configurando ambiente virtual e instalando pacotes..." -ForegroundColor Cyan
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& ".\.venv\Scripts\Activate.ps1"

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

Write-Host "==> [3/3] Gerando o executavel standalone com Flet/PyInstaller..." -ForegroundColor Cyan
flet pack --name "GeradorAgenda" --hidden-import odfdo --onedir -y scripts\gui_agenda.py

Write-Host "==> Sucesso! Executavel disponivel em: dist\GeradorAgenda\GeradorAgenda.exe" -ForegroundColor Green
