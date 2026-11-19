#!/usr/bin/env bash
set -e

# Raiz do projeto
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Verificando ambiente virtual..."
if [ ! -d ".venv" ]; then
    echo "Erro: Ambiente virtual .venv não encontrado na raiz."
    exit 1
fi

echo "==> Gerando o aplicativo macOS (.app) via Flet/PyInstaller..."
./.venv/bin/flet pack \
    --name "GeradorAgenda" \
    --hidden-import odfdo \
    -y \
    scripts/gui_agenda.py

echo "==> Gerando instalador .dmg (Drag-and-Drop para /Applications)..."
STAGING_DIR="dist/dmg_staging"
MACHINE_ARCH="${MACOS_ARCH:-$(uname -m)}"
case "$MACHINE_ARCH" in
    arm64|aarch64|Apple-Silicon) INSTALLER_ARCH="Apple-Silicon" ;;
    x86_64|x64|Intel) INSTALLER_ARCH="Intel" ;;
    *) echo "Arquitetura macOS não reconhecida: $MACHINE_ARCH" >&2; exit 1 ;;
esac
INSTALLER_PATH="dist/GeradorAgenda-Instalador-macOS-${INSTALLER_ARCH}.dmg"
rm -rf "$STAGING_DIR" "$INSTALLER_PATH"
mkdir -p "$STAGING_DIR"
cp -R dist/GeradorAgenda.app "$STAGING_DIR/"
ln -s /Applications "$STAGING_DIR/Applications"

hdiutil detach "/Volumes/Gerador de Agenda" 2>/dev/null || true

hdiutil create \
    -volname "Gerador de Agenda" \
    -srcfolder "$STAGING_DIR" \
    -ov \
    -format UDZO \
    -fs HFS+ \
    "$INSTALLER_PATH"

rm -rf "$STAGING_DIR"

echo "==> Concluído com sucesso!"
echo "    App:        dist/GeradorAgenda.app"
echo "    Instalador: $INSTALLER_PATH"
