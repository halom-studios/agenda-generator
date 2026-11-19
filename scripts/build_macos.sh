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
rm -rf "$STAGING_DIR" dist/GeradorAgenda-Instalador.dmg
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
    dist/GeradorAgenda-Instalador.dmg

rm -rf "$STAGING_DIR"

echo "==> Concluído com sucesso!"
echo "    App:        dist/GeradorAgenda.app"
echo "    Instalador: dist/GeradorAgenda-Instalador.dmg"
