import flet as ft
import os
import sys
import datetime
import asyncio

# Import our backend logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from leitor_clozes import extract_verses
from gerador_agenda import create_agenda, parse_flexible_date

async def main(page: ft.Page):
    page.title = "Gerador de Cadernos e Agendas"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 650
    page.window.height = 700
    page.scroll = ft.ScrollMode.AUTO

    # Variables to store paths and state
    selected_files = [] # list of dicts: {"path": str, "theme_input": TextField, "row": Row}
    state = {"template_path": None}

    # Status Text
    txt_status = ft.Text(value="Aguardando arquivos...", color="grey")

    verses_list_view = ft.ListView(spacing=5, height=140, width=540)

    # Register FilePicker services in modern Flet 1.x
    pick_verses_dialog = ft.FilePicker()
    pick_template_dialog = ft.FilePicker()
    page.services.extend([pick_verses_dialog, pick_template_dialog])

    # UI Elements for selections
    lbl_template = ft.Text(value="Nenhum arquivo selecionado", italic=True)

    # Actions with async/await (Flet 1.x standard)
    async def open_verses_picker(e):
        print("[DEBUG] Botão Adicionar Markdown(s) clicado.")
        try:
            files = await pick_verses_dialog.pick_files(
                dialog_title="Selecione os arquivos de Versículos (.md)",
                allow_multiple=True,
                file_type=ft.FilePickerFileType.ANY
            )
            print(f"[DEBUG] Arquivos selecionados: {files}")
            if files:
                invalid_files = []
                for f in files:
                    if not f.path.lower().endswith((".md", ".markdown", ".txt")):
                        invalid_files.append(os.path.basename(f.path))
                        continue
                    # Check if already added
                    if not any(item["path"] == f.path for item in selected_files):
                        theme_input = ft.TextField(label="Tema (ex: Relacional)", width=150, height=40, text_size=12)

                        def remove_file(path_to_remove):
                            def on_click(ev):
                                for item in selected_files:
                                    if item["path"] == path_to_remove:
                                        selected_files.remove(item)
                                        verses_list_view.controls.remove(item["row"])
                                        break
                                if not selected_files:
                                    txt_status.value = "Aguardando arquivos..."
                                    txt_status.color = "grey"
                                else:
                                    txt_status.value = f"{len(selected_files)} arquivo(s) selecionado(s)."
                                page.update()
                            return on_click

                        row = ft.Row([
                            ft.Text(os.path.basename(f.path), width=160, tooltip=f.path, size=12),
                            theme_input,
                            ft.IconButton(icon=ft.Icons.DELETE, on_click=remove_file(f.path), tooltip="Remover", icon_size=16)
                        ], alignment=ft.MainAxisAlignment.CENTER)

                        selected_files.append({"path": f.path, "theme_input": theme_input, "row": row})
                        verses_list_view.controls.append(row)

                if invalid_files:
                    txt_status.value = f"{len(selected_files)} arquivo(s) adicionado(s). Ignorados (não são .md): {', '.join(invalid_files)}"
                    txt_status.color = "orange"
                else:
                    txt_status.value = f"{len(selected_files)} arquivo(s) selecionado(s)."
                    txt_status.color = "blue"
                page.update()
        except Exception as ex:
            print(f"[ERRO] Falha ao abrir picker de versículos: {ex}")
            txt_status.value = f"Erro ao selecionar versículos: {ex}"
            txt_status.color = "red"
            page.update()

    async def open_template_picker(e):
        print("[DEBUG] Botão Selecionar Template clicado.")
        try:
            files = await pick_template_dialog.pick_files(
                dialog_title="Selecione o template LibreOffice (.odg)",
                allow_multiple=False,
                file_type=ft.FilePickerFileType.ANY
            )
            print(f"[DEBUG] Template selecionado: {files}")
            if files:
                file_path = files[0].path
                if not file_path.lower().endswith(".odg"):
                    txt_status.value = f"Aviso: selecione um arquivo de template .odg válido (selecionado: {os.path.basename(file_path)})"
                    txt_status.color = "red"
                    page.update()
                    return
                state["template_path"] = file_path
                lbl_template.value = os.path.basename(file_path)
                txt_status.value = f"Template selecionado: {os.path.basename(file_path)}"
                txt_status.color = "blue"
                page.update()
        except Exception as ex:
            print(f"[ERRO] Falha ao abrir picker de template: {ex}")
            txt_status.value = f"Erro ao selecionar template: {ex}"
            txt_status.color = "red"
            page.update()

    # Form elements for Date Range Selection
    current_year = datetime.datetime.now().year
    default_start_val = f"01/11/{current_year}"
    default_end_val = f"31/12/{current_year + 1}"

    txt_start_date = ft.TextField(
        label="Data Inicial", 
        value=default_start_val, 
        hint_text="Ex: 01/11/2026 ou nov 2026",
        width=175,
        height=40,
        text_size=12
    )

    txt_end_date = ft.TextField(
        label="Data Final", 
        value=default_end_val, 
        hint_text="Ex: 31/12/2027 ou dez 2027",
        width=175,
        height=40,
        text_size=12
    )

    lbl_date_info = ft.Text(value="", size=12, italic=True)

    def update_date_info():
        try:
            d_s = parse_flexible_date(txt_start_date.value, is_end_date=False)
            d_e = parse_flexible_date(txt_end_date.value, is_end_date=True)
            if d_e >= d_s:
                total_days = (d_e - d_s).days + 1
                lbl_date_info.value = f"📅 Período: {d_s.strftime('%d/%m/%Y')} a {d_e.strftime('%d/%m/%Y')} ({total_days} dias / páginas)"
                lbl_date_info.color = "blue"
            else:
                lbl_date_info.value = "⚠️ Data final não pode ser anterior à data inicial."
                lbl_date_info.color = "red"
        except Exception as ex:
            lbl_date_info.value = f"Formato de data: use DD/MM/AAAA ou MM/AAAA ({ex})"
            lbl_date_info.color = "grey"
        page.update()

    txt_start_date.on_change = lambda e: update_date_info()
    txt_end_date.on_change = lambda e: update_date_info()

    # Native DatePickers
    dp_start = ft.DatePicker()
    dp_end = ft.DatePicker()
    page.overlay.extend([dp_start, dp_end])

    def on_dp_start_change(e):
        if dp_start.value:
            txt_start_date.value = dp_start.value.strftime("%d/%m/%Y")
            update_date_info()

    def on_dp_end_change(e):
        if dp_end.value:
            txt_end_date.value = dp_end.value.strftime("%d/%m/%Y")
            update_date_info()

    dp_start.on_change = on_dp_start_change
    dp_end.on_change = on_dp_end_change

    def open_dp_start(e):
        dp_start.open = True
        page.update()

    def open_dp_end(e):
        dp_end.open = True
        page.update()

    # Container with Date Inputs
    container_dates = ft.Column(
        [
            ft.Text("Configuração de Período", weight="bold"),
            ft.Row(
                [
                    txt_start_date,
                    ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, tooltip="Calendário inicial", on_click=open_dp_start),
                    ft.Container(width=10),
                    txt_end_date,
                    ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, tooltip="Calendário final", on_click=open_dp_end),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            lbl_date_info,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
    )

    # Container with Verses Inputs
    container_verses = ft.Column(
        [
            ft.Text("Arquivos de Versículos (.md)", weight="bold"),
            ft.Row(
                [
                    ft.Button(
                        "Adicionar Markdown(s)", 
                        icon=ft.Icons.LIBRARY_ADD, 
                        on_click=open_verses_picker
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER
            ),
            verses_list_view,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
    )

    # Mode selection
    mode_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="agenda", label="Agenda (Datas + Versículos)"),
            ft.Radio(value="dates_only", label="Só Datas"),
            ft.Radio(value="notebook", label="Só Versículos (Caderno)"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="agenda"
    )

    def on_mode_change(e):
        selected = mode_radio.value
        if selected == "agenda":
            container_dates.visible = True
            container_verses.visible = True
        elif selected == "dates_only":
            container_dates.visible = True
            container_verses.visible = False
        else: # notebook
            container_dates.visible = False
            container_verses.visible = True
        page.update()

    mode_radio.on_change = on_mode_change

    async def generate_clicked(e):
        print("Botão Gerar clicado.")
        selected_mode = mode_radio.value

        # Validação de versículos se for agenda ou notebook
        if selected_mode in ("agenda", "notebook"):
            if not selected_files:
                txt_status.value = "ERRO: Selecione ao menos um arquivo de versículos (Markdown)."
                txt_status.color = "red"
                page.update()
                return

        # Validação de template obrigatória para todos os modos
        if not state["template_path"]:
            txt_status.value = "ERRO: Selecione o arquivo de template (ODG)."
            txt_status.color = "red"
            page.update()
            return

        # Validação de datas
        d_start, d_end = None, None
        if selected_mode in ("agenda", "dates_only"):
            try:
                d_start = parse_flexible_date(txt_start_date.value, is_end_date=False)
                d_end = parse_flexible_date(txt_end_date.value, is_end_date=True)
                if d_end < d_start:
                    txt_status.value = "ERRO: A data final não pode ser menor que a data inicial."
                    txt_status.color = "red"
                    page.update()
                    return
            except Exception as ex:
                txt_status.value = f"ERRO na data: {ex}"
                txt_status.color = "red"
                page.update()
                return

        # Disable button to prevent double click
        btn_generate.disabled = True
        txt_status.value = "Gerando... Aguarde."
        txt_status.color = "orange"
        page.update()

        try:
            # 1. Extração de versículos se aplicável
            all_verses = []
            if selected_mode in ("agenda", "notebook") and selected_files:
                for item in selected_files:
                    verses_from_file = extract_verses(item["path"])
                    theme_val = item["theme_input"].value.strip()
                    for v in verses_from_file:
                        v["tema"] = theme_val
                    all_verses.extend(verses_from_file)

                if not all_verses:
                    txt_status.value = "ERRO: Nenhum versículo encontrado nos arquivos selecionados."
                    txt_status.color = "red"
                    btn_generate.disabled = False
                    page.update()
                    return

            # 2. Definição do Diretório e Nome do Arquivo de Saída
            if selected_files:
                base_dir = os.path.dirname(selected_files[0]["path"])
                if len(selected_files) == 1:
                    base_name = os.path.splitext(os.path.basename(selected_files[0]["path"]))[0]
                else:
                    base_name = "Combinados"
            else:
                base_dir = os.path.dirname(state["template_path"])
                base_name = "Datas"

            if selected_mode == "notebook":
                output_file = os.path.join(base_dir, f"Caderno_{base_name}.odg")
            elif selected_mode == "dates_only":
                output_file = os.path.join(base_dir, f"Agenda_Datas_{d_start.strftime('%Y%m%d')}_{d_end.strftime('%Y%m%d')}.odg")
            else:
                output_file = os.path.join(base_dir, f"Agenda_{d_start.strftime('%Y%m%d')}_{d_end.strftime('%Y%m%d')}_{base_name}.odg")

            # 3. Execução em segundo plano para não travar a interface
            await asyncio.to_thread(
                create_agenda,
                verses=all_verses,
                output_filename=output_file,
                template_path=state["template_path"],
                mode=selected_mode,
                start_date=d_start,
                end_date=d_end
            )

            txt_status.value = f"SUCESSO! Arquivo salvo em:\n{output_file}"
            txt_status.color = "green"

        except Exception as ex:
            txt_status.value = f"ERRO FATAL: {str(ex)}"
            txt_status.color = "red"

        btn_generate.disabled = False
        page.update()

    btn_generate = ft.Button(
        content="Gerar ODG",
        icon=ft.Icons.SETTINGS_SUGGEST,
        on_click=generate_clicked,
        height=50,
        width=250
    )

    # Initial state calculation
    update_date_info()

    # Layout Construction
    page.add(
        ft.Column(
            [
                ft.Text("Gerador de Cadernos e Agendas", size=24, weight="bold"),
                ft.Text("Tags disponíveis: {{dia}}, {{mes}}, {{ano}}, {{semana}}, {{data}}, {{versiculo}}, {{referencia}}, {{tema}}", size=11, color="grey"),
                ft.Divider(),

                ft.Text("Modo de Geração", weight="bold"),
                mode_radio,
                ft.Container(height=10),

                container_dates,
                ft.Container(height=10),

                ft.Divider(),

                container_verses,

                ft.Container(height=15),

                ft.Text("Template LibreOffice (.odg)", weight="bold"),
                ft.Row(
                    [
                        ft.Button(
                            "Selecionar Template", 
                            icon=ft.Icons.IMAGE, 
                            on_click=open_template_picker
                        ),
                        lbl_template,
                    ], alignment=ft.MainAxisAlignment.CENTER
                ),

                ft.Divider(),
                ft.Container(height=10),

                btn_generate,

                ft.Container(height=15),
                txt_status,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.run(main)
