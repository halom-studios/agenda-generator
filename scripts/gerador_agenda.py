import sys
import os
import copy
import datetime
import calendar
import re
import locale
from odfdo import Document, DrawPage, Frame, Paragraph, Style

# Try to set locale to Portuguese for localized month and weekday names
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, '') # Fallback to system default
    except locale.Error:
        pass

# Import the reader script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from leitor_clozes import extract_verses

WEEKDAYS_PT = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]

MONTHS_NAMES_PT = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

MONTHS_PT_MAP = {
    "jan": 1, "janeiro": 1,
    "fev": 2, "fevereiro": 2,
    "mar": 3, "marco": 3, "março": 3,
    "abr": 4, "abril": 4,
    "mai": 5, "maio": 5,
    "jun": 6, "junho": 6,
    "jul": 7, "julho": 7,
    "ago": 8, "agosto": 8,
    "set": 9, "setembro": 9,
    "out": 10, "outubro": 10,
    "nov": 11, "novembro": 11,
    "dez": 12, "dezembro": 12
}

def parse_flexible_date(val, is_end_date: bool = False) -> datetime.date:
    """
    Interpreta formatos de data flexíveis:
    - DD/MM/AAAA ou DD-MM-AAAA
    - AAAA-MM-DD
    - MM/AAAA (se for fim, vai até o último dia do mês)
    - "novembro 2026", "dez/2027"
    - Apenas o ano: "2027"
    """
    if isinstance(val, datetime.date):
        return val
    if isinstance(val, datetime.datetime):
        return val.date()

    val = str(val).strip().lower()

    # DD/MM/AAAA
    m = re.match(r"^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$", val)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return datetime.date(year, month, day)

    # AAAA-MM-DD
    m = re.match(r"^(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})$", val)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return datetime.date(year, month, day)

    # MM/AAAA
    m = re.match(r"^(\d{1,2})[/.-](\d{4})$", val)
    if m:
        month, year = int(m.group(1)), int(m.group(2))
        day = calendar.monthrange(year, month)[1] if is_end_date else 1
        return datetime.date(year, month, day)

    # Nome do mês + Ano: "novembro 2026", "nov/2026", "novembro-2026"
    m = re.match(r"^([a-zçãéíóú]+)[/\s-]+(\d{4})$", val)
    if m:
        m_name, year = m.group(1), int(m.group(2))
        for k, v in MONTHS_PT_MAP.items():
            if m_name.startswith(k):
                day = calendar.monthrange(year, v)[1] if is_end_date else 1
                return datetime.date(year, v, day)

    # Apenas o ano: "2027"
    m = re.match(r"^(\d{4})$", val)
    if m:
        year = int(m.group(1))
        return datetime.date(year, 12, 31) if is_end_date else datetime.date(year, 1, 1)

    raise ValueError(f"Formato de data inválido: '{val}'. Use DD/MM/AAAA ou MM/AAAA (ex: 01/11/2026 ou novembro 2026).")

def replace_tags_in_page(page, replacements: dict):
    """
    Substitui todas as tags mapeadas em replacements de uma só vez nos parágrafos da página.
    Remove elementos filhos (como text:span) para desfragmentar o parágrafo editado pelo LibreOffice.
    """
    found = False
    paragraphs = page.get_elements('//text:p')
    for p in paragraphs:
        text = p.inner_text
        changed = False
        for key, val in replacements.items():
            if key in text:
                text = text.replace(key, str(val))
                changed = True
        if changed:
            for child in list(p.children):
                p.delete(child)
            p.text = text
            found = True
    return found

def replace_text_in_page(page, key, value):
    """Compatibilidade retroativa com código existente"""
    return replace_tags_in_page(page, {key: value})

def create_agenda(
    verses=None, 
    output_filename="Agenda_Vida_de_Fe.odg", 
    template_path=None, 
    mode="agenda", 
    start_date=None, 
    end_date=None, 
    year=None
):
    if not template_path or not os.path.exists(template_path):
        raise FileNotFoundError(f"Template não encontrado em: {template_path}")

    # Load template
    doc = Document(template_path)
    body = doc.body
    
    # Get all master pages from the template
    master_pages = []
    i = 0
    while True:
        try:
            page = body.get_draw_page(i)
            if page:
                master_pages.append(page)
                i += 1
            else:
                break
        except Exception:
            break
            
    if not master_pages:
        raise ValueError("Nenhuma página encontrada no template ODG.")
    
    verses = verses or []
    pages_to_add = []
    
    if mode == "notebook":
        if not verses:
            raise ValueError("Modo Caderno exige ao menos um versículo nos arquivos Markdown.")

        for i, verse in enumerate(verses):
            master_page = master_pages[i % len(master_pages)]
            new_page = master_page.clone
            new_page.name = f"Page_{i+1}"
            
            replacements = {
                "{{versiculo}}": verse.get('text', ''),
                "{{referencia}}": verse.get('reference', ''),
                "{{tema}}": verse.get('tema', ''),
                "{{dia}}": "",
                "{{mes}}": "",
                "{{ano}}": "",
                "{{semana}}": "",
                "{{dia_semana}}": "",
                "{{data}}": "",
            }
            replace_tags_in_page(new_page, replacements)
            pages_to_add.append(new_page)
            
    elif mode in ("agenda", "dates_only"):
        # Resolve intervalo de datas
        if start_date:
            d_start = parse_flexible_date(start_date, is_end_date=False)
        elif year:
            d_start = datetime.date(year, 1, 1)
        else:
            d_start = datetime.date(datetime.datetime.now().year + 1, 1, 1)

        if end_date:
            d_end = parse_flexible_date(end_date, is_end_date=True)
        elif year:
            d_end = datetime.date(year, 12, 31)
        else:
            d_end = datetime.date(d_start.year, 12, 31)

        if d_end < d_start:
            raise ValueError(f"A data final ({d_end.strftime('%d/%m/%Y')}) deve ser posterior ou igual à data inicial ({d_start.strftime('%d/%m/%Y')}).")

        total_days = (d_end - d_start).days + 1
        
        for i in range(total_days):
            current_date = d_start + datetime.timedelta(days=i)
            master_page = master_pages[i % len(master_pages)]
            new_page = master_page.clone
            new_page.name = f"Page_{i+1}_{current_date.strftime('%Y%m%d')}"
            
            # Formatações das tags de data
            day_str = f"{current_date.day:02d}"
            month_str = MONTHS_NAMES_PT[current_date.month - 1]
            year_str = str(current_date.year)
            weekday_str = WEEKDAYS_PT[current_date.weekday()]
            full_date_str = f"{current_date.day:02d}/{current_date.month:02d}/{current_date.year}"
            
            replacements = {
                "{{dia}}": day_str,
                "{{mes}}": month_str,
                "{{ano}}": year_str,
                "{{semana}}": weekday_str,
                "{{dia_semana}}": weekday_str,
                "{{data}}": full_date_str,
            }
            
            if mode == "dates_only":
                # Limpa tags de versículos se existirem no template
                replacements["{{versiculo}}"] = ""
                replacements["{{referencia}}"] = ""
                replacements["{{tema}}"] = ""
            else:
                # Modo agenda com versículos
                if verses:
                    verse = verses[i % len(verses)]
                    replacements["{{versiculo}}"] = verse.get('text', '')
                    replacements["{{referencia}}"] = verse.get('reference', '')
                    replacements["{{tema}}"] = verse.get('tema', '')
                else:
                    replacements["{{versiculo}}"] = ""
                    replacements["{{referencia}}"] = ""
                    replacements["{{tema}}"] = ""
            
            replace_tags_in_page(new_page, replacements)
            pages_to_add.append(new_page)
    else:
        raise ValueError(f"Modo desconhecido: '{mode}'. Opções: 'agenda', 'dates_only', 'notebook'.")

    # Substitui as master pages pelas novas páginas geradas mantendo a estrutura XML
    container = master_pages[0].parent
    for p in master_pages:
        container.delete(p)
        
    for p in pages_to_add:
        container.append(p)
        
    doc.save(output_filename)
    print(f"Salvo {output_filename} com {len(pages_to_add)} páginas.")
    return output_filename
