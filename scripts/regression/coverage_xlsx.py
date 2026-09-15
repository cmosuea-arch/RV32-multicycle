#!/usr/bin/env python3
"""Create a formatted XLSX workbook from the ISA coverage CSV using stdlib only."""
from collections import OrderedDict
import csv
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


LABELS = {
    'Register': 'Aritmética e lógica — registradores',
    'Immediate': 'Aritmética e lógica — imediatos',
    'Upper': 'Imediatos superiores',
    'Branch': 'Desvios condicionais',
    'Jump': 'Saltos',
    'Load': 'Leitura de memória',
    'Store': 'Escrita de memória',
    'Multiplication': 'Multiplicação — Zmmul',
    'CRC': 'CRC — Xicrc',
    'Sistema/Sincronização': 'Sistema/Sincronização',
}


def column_name(index):
    name = ''
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def cell(reference, value, style=0, number=False):
    if number:
        return f'<c r="{reference}" s="{style}"><v>{value}</v></c>'
    text = escape(str(value))
    preserve = ' xml:space="preserve"' if text.startswith(' ') or text.endswith(' ') else ''
    return f'<c r="{reference}" s="{style}" t="inlineStr"><is><t{preserve}>{text}</t></is></c>'


def row_xml(number, values, styles=None, numbers=None, height=None):
    styles = styles or {}
    numbers = numbers or set()
    attrs = f' r="{number}"'
    if height:
        attrs += f' ht="{height}" customHeight="1"'
    cells = ''.join(cell(f'{column_name(index)}{number}', value,
                         styles.get(index, 0), index in numbers)
                    for index, value in enumerate(values, 1))
    return f'<row{attrs}>{cells}</row>'


def worksheet(rows, widths, freeze_row=1, autofilter=None, table=False):
    max_row = len(rows)
    max_col = max(len(values) for values, _, _, _ in rows)
    dimension = f'A1:{column_name(max_col)}{max_row}'
    columns = ''.join(f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>'
                      for i, width in enumerate(widths, 1))
    pane = (f'<pane ySplit="{freeze_row}" topLeftCell="A{freeze_row + 1}" '
            f'activePane="bottomLeft" state="frozen"/>') if freeze_row else ''
    selection = '<selection pane="bottomLeft" activeCell="A2" sqref="A2"/>' if freeze_row else ''
    sheet_rows = ''.join(row_xml(i, *record) for i, record in enumerate(rows, 1))
    filter_xml = f'<autoFilter ref="{autofilter}"/>' if autofilter else ''
    table_xml = '<tableParts count="1"><tablePart r:id="rId1"/></tableParts>' if table else ''
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <dimension ref="{dimension}"/><sheetViews><sheetView workbookViewId="0">{pane}{selection}</sheetView></sheetViews>
 <sheetFormatPr defaultRowHeight="15"/><cols>{columns}</cols><sheetData>{sheet_rows}</sheetData>
 {filter_xml}<pageMargins left="0.25" right="0.25" top="0.5" bottom="0.5" header="0.2" footer="0.2"/>
 <pageSetup orientation="landscape" fitToWidth="1" fitToHeight="0"/>{table_xml}
</worksheet>'''


def zip_write(archive, name, content):
    info = ZipInfo(name, (2026, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    archive.writestr(info, content.encode('utf-8'))


def generate_xlsx(csv_path, output_path):
    csv_path, output_path = Path(csv_path), Path(output_path)
    with csv_path.open(newline='', encoding='utf-8') as source:
        data = list(csv.DictReader(source))
    if not data:
        raise ValueError('coverage CSV is empty')
    headers = list(data[0])
    groups = OrderedDict()
    for item in data:
        groups.setdefault(item['Categoria'], []).append(item)

    summary = [
        (['Cobertura ISA — ChampionCHIP'], {1: 5}, set(), 26),
        (['Categoria', 'Implementadas', 'Esperadas', 'Cobertura'], {1: 1, 2: 1, 3: 1, 4: 1}, set(), 22),
    ]
    total_passed = 0
    for category, items in groups.items():
        passed = sum(all(item[key] == 'PASS' for key in
                         ('Teste unitário', 'Teste integrado', 'Regressão')) for item in items)
        total_passed += passed
        summary.append(([LABELS.get(category, category), passed, len(items), passed / len(items)],
                        {4: 4}, {2, 3, 4}, None))
    summary.append((['TOTAL', total_passed, len(data), total_passed / len(data)],
                    {1: 2, 2: 2, 3: 2, 4: 6}, {2, 3, 4}, 22))
    summary += [
        ([], {}, set(), None),
        (['Estado geral', f'{total_passed}/{len(data)} instruções'], {1: 3, 2: 3}, set(), None),
        (['Firmware oficial', 'PENDENTE'], {1: 3, 2: 7}, set(), None),
        (['Observação', 'O firmware próprio não substitui a validação oficial.'], {1: 3}, set(), 30),
    ]

    detail = [(headers, {index: 1 for index in range(1, len(headers) + 1)}, set(), 30)]
    for item in data:
        values = [item[header] for header in headers]
        styles = {}
        for index, value in enumerate(values, 1):
            if value == 'PASS':
                styles[index] = 3
            elif value == 'PENDENTE':
                styles[index] = 7
        detail.append((values, styles, set(), 30 if item['Evidência'] or item['Observação'] else None))

    summary_xml = worksheet(summary, [40, 18, 14, 16], freeze_row=2,
                            autofilter=f'A2:D{2 + len(groups)}')
    last_col = column_name(len(headers))
    detail_xml = worksheet(detail, [23, 14, 12, 10, 10, 24, 16, 16, 14, 18, 16, 64, 44],
                           freeze_row=1, table=True)
    table_columns = ''.join(f'<tableColumn id="{index}" name="{escape(header)}"/>'
                            for index, header in enumerate(headers, 1))
    table = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<table xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" id="1" name="TabelaCobertura"
 displayName="TabelaCobertura" ref="A1:{last_col}{len(detail)}" totalsRowShown="0">
 <autoFilter ref="A1:{last_col}{len(detail)}"/><tableColumns count="{len(headers)}">{table_columns}</tableColumns>
 <tableStyleInfo name="TableStyleMedium2" showFirstColumn="0" showLastColumn="0" showRowStripes="1" showColumnStripes="0"/>
</table>'''

    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="xml" ContentType="application/xml"/>
 <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
 <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
 <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
 <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
 <Override PartName="/xl/tables/table1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.table+xml"/>
 <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
 <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
 <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
 <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''
    workbook = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <bookViews><workbookView/></bookViews><sheets>
  <sheet name="Resumo" sheetId="1" r:id="rId1"/><sheet name="Instruções" sheetId="2" r:id="rId2"/>
 </sheets><calcPr calcId="191029"/></workbook>'''
    workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
 <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
 <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''
    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
 <numFmts count="0"/><fonts count="3">
  <font><sz val="10"/><name val="Aptos"/></font>
  <font><b/><color rgb="FFFFFFFF"/><sz val="10"/><name val="Aptos"/></font>
  <font><b/><color rgb="FF17365D"/><sz val="16"/><name val="Aptos Display"/></font>
 </fonts><fills count="6">
  <fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>
  <fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/><bgColor indexed="64"/></patternFill></fill>
  <fill><patternFill patternType="solid"><fgColor rgb="FFC6EFCE"/><bgColor indexed="64"/></patternFill></fill>
  <fill><patternFill patternType="solid"><fgColor rgb="FFFFEB9C"/><bgColor indexed="64"/></patternFill></fill>
  <fill><patternFill patternType="solid"><fgColor rgb="FFD9EAF7"/><bgColor indexed="64"/></patternFill></fill>
 </fills><borders count="2"><border/><border><left style="thin"><color rgb="FFD9E1F2"/></left><right style="thin"><color rgb="FFD9E1F2"/></right><top style="thin"><color rgb="FFD9E1F2"/></top><bottom style="thin"><color rgb="FFD9E1F2"/></bottom><diagonal/></border></borders>
 <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
 <cellXfs count="8">
  <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
  <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
  <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyAlignment="1"><alignment vertical="center"/></xf>
  <xf numFmtId="0" fontId="0" fillId="3" borderId="1" xfId="0" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
  <xf numFmtId="10" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment horizontal="center"/></xf>
  <xf numFmtId="0" fontId="2" fillId="5" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="center"/></xf>
  <xf numFmtId="10" fontId="1" fillId="2" borderId="1" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment horizontal="center"/></xf>
  <xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
 </cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''
    sheet2_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/table" Target="../tables/table1.xml"/>
</Relationships>'''
    core = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <dc:title>Cobertura ISA CMOS RISC-V</dc:title><dc:creator>Projeto CMOS RISC-V</dc:creator>
 <dc:description>Cobertura gerada automaticamente de coverage.csv</dc:description>
</cp:coreProperties>'''
    app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>CMOS coverage generator</Application></Properties>'''

    with ZipFile(output_path, 'w') as archive:
        for name, content in [
            ('[Content_Types].xml', content_types), ('_rels/.rels', root_rels),
            ('xl/workbook.xml', workbook), ('xl/_rels/workbook.xml.rels', workbook_rels),
            ('xl/styles.xml', styles), ('xl/worksheets/sheet1.xml', summary_xml),
            ('xl/worksheets/sheet2.xml', detail_xml),
            ('xl/worksheets/_rels/sheet2.xml.rels', sheet2_rels),
            ('xl/tables/table1.xml', table), ('docProps/core.xml', core),
            ('docProps/app.xml', app),
        ]:
            zip_write(archive, name, content)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    generate_xlsx(root / 'docs/isa/coverage.csv', root / 'docs/isa/coverage.xlsx')
