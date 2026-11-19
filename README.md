# Gerador de Cadernos e Agendas

Aplicativo desktop em Python para gerar agendas e cadernos em formato ODG (LibreOffice Draw), usando um template `.odg` e, opcionalmente, arquivos Markdown com versículos.

## Recursos

- Geração de agenda com datas e versículos.
- Geração somente de datas.
- Geração de caderno somente com versículos.
- Datas em formatos como `DD/MM/AAAA`, `MM/AAAA`, `novembro 2026` ou `2027`.
- Substituição das tags do template: `{{dia}}`, `{{mes}}`, `{{ano}}`, `{{semana}}`, `{{dia_semana}}`, `{{data}}`, `{{versiculo}}`, `{{referencia}}` e `{{tema}}`.

## Requisitos

- Python 3.10 ou superior.
- Um template compatível `.odg` criado no LibreOffice Draw.

## Executar a partir do código

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/gui_agenda.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/gui_agenda.py
```

Na interface, selecione o modo, os arquivos Markdown quando necessários e o template `.odg`. O arquivo de saída é salvo junto aos arquivos Markdown selecionados ou, quando nenhum Markdown é necessário, junto ao template.

### Formato de versículos Markdown

O leitor reconhece blocos no formato Obsidian abaixo:

```markdown
>[!Bible] João 3:16 (NVI)
>Porque Deus tanto amou o mundo...
```

## Criar executável Windows

No Windows, execute `scripts\build_windows.bat` ou `scripts\build_windows.ps1`. O processo instala as dependências e empacota o aplicativo com Flet. A saída esperada é `dist\GeradorAgenda\GeradorAgenda.exe`; o instalador fica em `dist\GeradorAgenda-Instalador-Windows.exe`.

Para gerar também um instalador, instale o [Inno Setup](https://jrsoftware.org/isinfo.php) e compile `scripts\installer_windows.iss` depois de gerar a pasta do aplicativo em `dist/GeradorAgenda/`.

## Criar aplicativo macOS

Com as dependências instaladas em `.venv`, execute:

```bash
bash scripts/build_macos.sh
```

O script cria o `.app` e uma imagem `.dmg` em `dist/`.

## GitHub Actions

O workflow `.github/workflows/windows-installer.yml` roda em pushes para `main`, pull requests para `main` e também pode ser iniciado manualmente pela aba **Actions**. Cada execução bem-sucedida gera o instalador Inno Setup e disponibiliza os arquivos em **Artifacts** por 14 dias. O workflow aplica uma correção temporária e verificada para um bug do Flet CLI 1.1.2 ao atualizar metadados do executável no Windows.

Para publicar o instalador em um GitHub Release, crie e envie uma tag começando com `v`, por exemplo `v1.0.0`. Nessa execução, o instalador também será anexado ao Release. O workflow usa as permissões padrão `GITHUB_TOKEN` declaradas no próprio arquivo; nenhum secret adicional é necessário.

## Estrutura

```text
scripts/
  gui_agenda.py       # Interface gráfica
  gerador_agenda.py   # Geração dos documentos ODG
  leitor_clozes.py    # Extração dos versículos do Markdown
  build_windows.bat
  build_windows.ps1
  build_macos.sh
  installer_windows.iss
.github/workflows/
  windows-installer.yml
```

## Licença

Ainda não definida. Defina uma licença antes de distribuir o projeto publicamente.
