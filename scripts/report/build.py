#!/usr/bin/env python3
"""Exporta o rascunho Markdown para PDF, sem executar testes ou alterar evidências."""
# Ferramenta editorial separada da regressão: lê texto/figuras já existentes.
import argparse
from html import escape
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote

from markdown_it import MarkdownIt
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[2]
WIDTH = A4[0] - 92


def inline(token):
    """Converte apenas a marcação usada no relatório, escapando texto literal."""
    parts = []
    for child in token.children or []:
        kind = child.type
        if kind == 'text':
            parts.append(escape(child.content))
        elif kind in ('softbreak', 'hardbreak'):
            parts.append(' ' if kind == 'softbreak' else '<br/>')
        elif kind == 'code_inline':
            parts.append('<font name="Mono">' + escape(child.content) + '</font>')
        elif kind in ('strong_open', 'strong_close', 'em_open', 'em_close'):
            parts.append({'strong_open': '<b>', 'strong_close': '</b>',
                          'em_open': '<i>', 'em_close': '</i>'}[kind])
        elif kind == 'link_open':
            parts.append('<link color="#155878" href="' +
                         escape(child.attrGet('href'), quote=True) + '">')
        elif kind == 'link_close':
            parts.append('</link>')
        else:
            raise ValueError(f'Marcação inline não suportada: {kind}')
    return ''.join(parts)


def main():
    # Permite escolher Markdown, destino PDF e diretório das fontes pelo terminal.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path,
                        default=ROOT / 'docs/report/relatorio.md')
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'docs/report/relatorio-preliminar.pdf')
    parser.add_argument('--font-dir', type=Path,
                        default=Path('/usr/share/fonts/truetype/dejavu'))
    args = parser.parse_args()

    # Fontes Unicode incorporadas mantêm acentos e permitem leitura sem fontes locais.
    for name, filename in [('Body', 'DejaVuSans.ttf'),
                           ('BodyBold', 'DejaVuSans-Bold.ttf'),
                           ('BodyItalic', 'DejaVuSans-Oblique.ttf'),
                           ('BodyBoldItalic', 'DejaVuSans-BoldOblique.ttf'),
                           ('Mono', 'DejaVuSansMono.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(args.font_dir / filename)))
    pdfmetrics.registerFontFamily('Body', normal='Body', bold='BodyBold',
                                  italic='BodyItalic', boldItalic='BodyBoldItalic')
    body = ParagraphStyle('body', fontName='Body', fontSize=9.4, leading=13.3,
                          spaceAfter=7, alignment=TA_LEFT)
    cell = ParagraphStyle('cell', parent=body, fontSize=8.1, leading=10.7,
                          spaceAfter=0)
    code = ParagraphStyle('code', fontName='Mono', fontSize=7.3, leading=9.7,
                          spaceBefore=4, spaceAfter=9)
    headings = {
        'h1': ParagraphStyle('h1', parent=body, fontName='BodyBold', fontSize=17,
                             leading=21, spaceAfter=14, keepWithNext=True),
        'h2': ParagraphStyle('h2', parent=body, fontName='BodyBold', fontSize=14,
                             leading=18, spaceAfter=10, keepWithNext=True),
        'h3': ParagraphStyle('h3', parent=body, fontName='BodyBold', fontSize=11,
                             leading=15, spaceBefore=7, spaceAfter=8,
                             keepWithNext=True),
    }
    # Markdown vira tokens; cada bloco vira um elemento ReportLab na sequência story.
    tokens = MarkdownIt('commonmark').enable('table').parse(args.source.read_text())
    story = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type in ('heading_open', 'paragraph_open'):
            children = tokens[i + 1].children or []
            if tok.type == 'paragraph_open' and len(children) == 1 and children[0].type == 'image':
                # Figuras locais são resolvidas em relação ao Markdown de origem.
                path = args.source.parent / unquote(children[0].attrGet('src'))
                figure = Image(str(path))
                scale = min(WIDTH / figure.imageWidth, 560 / figure.imageHeight)
                figure.drawWidth = figure.imageWidth * scale
                figure.drawHeight = figure.imageHeight * scale
                figure.hAlign = 'CENTER'
                story.extend([figure, Spacer(1, 8)])
                i += 3
                continue
            style = headings[tok.tag] if tok.type == 'heading_open' else body
            story.append(Paragraph(inline(tokens[i + 1]), style))
            i += 3
        elif tok.type == 'fence':
            # Impede que linhas de código/diagramas sejam cortadas horizontalmente.
            for line in tok.content.splitlines():
                if pdfmetrics.stringWidth(line, 'Mono', code.fontSize) > WIDTH:
                    raise ValueError(f'Linha de código larga demais: {line}')
            story.append(Preformatted(tok.content.rstrip(), code))
            i += 1
        elif tok.type == 'html_block' and tok.content.strip() == '<!-- pagebreak -->':
            story.append(PageBreak())
            i += 1
        elif tok.type == 'table_open':
            rows, row, lengths, minimums = [], [], [], []
            i += 1
            while tokens[i].type != 'table_close':
                item = tokens[i]
                if item.type == 'tr_open':
                    row = []
                elif item.type == 'inline':
                    col = len(row)
                    if len(lengths) <= col:
                        lengths.append(0)
                        minimums.append(0)
                    lengths[col] = max(lengths[col], min(len(item.content), 52))
                    # Reserva espaço para nomes de módulos/TBs e cabeçalhos inteiros.
                    plain = re.sub(r'[`*]', '', item.content)
                    minimums[col] = max(minimums[col], 12 + max(
                        (pdfmetrics.stringWidth(word, 'Body', cell.fontSize)
                         for word in plain.split()), default=0))
                    row.append(Paragraph(inline(item), cell))
                elif item.type == 'tr_close':
                    rows.append(row)
                i += 1
            # Distribui a largura restante sem cortar a maior palavra de cada coluna.
            weights = [max(12, n) for n in lengths]
            remaining = WIDTH - sum(minimums)
            if remaining < 0:
                raise ValueError('Tabela contém palavras longas demais para a página')
            widths = [minimum + remaining * n / sum(weights)
                      for minimum, n in zip(minimums, weights)]
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e1ecf2')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                 [colors.white, colors.HexColor('#f4f7f9')]),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#c5d1d8')),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 3.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
            ]))
            story.extend([table, Spacer(1, 9)])
            i += 1
        else:
            raise ValueError(f'Bloco Markdown não suportado: {tok.type}')

    def page_frame(canvas, doc):
        # Callback chamado em cada página para cabeçalho, versão e numeração.
        canvas.saveState()
        canvas.setFont('Body', 8)
        canvas.setFillColor(colors.HexColor('#50616f'))
        canvas.drawString(46, A4[1] - 28, 'CMOS RISC-V | ChampionCHIP — Fase 2')
        canvas.drawRightString(A4[0] - 46, A4[1] - 28, 'PRELIMINAR — NÃO SUBMETER')
        canvas.drawString(46, 27, 'Relatório de andamento | v0.6 | 27/10/2026')
        canvas.drawRightString(A4[0] - 46, 27, str(doc.page))
        canvas.restoreState()

    # Publica somente após construir e conferir o limite total, incluindo referências.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='cmos-report-') as temp:
        pdf = Path(temp) / 'report.pdf'
        doc = SimpleDocTemplate(str(pdf), pagesize=A4, leftMargin=46,
                                rightMargin=46, topMargin=49, bottomMargin=46,
                                title='CMOS RISC-V — Relatório preliminar Fase 2',
                                author='Equipe CMOS')
        doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
        count = len(PdfReader(pdf).pages)
        if count > 20:
            raise ValueError(f'PDF com {count} páginas; limite do guia: 20')
        args.output.write_bytes(pdf.read_bytes())
    print(f'PASS relatório: {count}/20 páginas; {args.output}')


if __name__ == '__main__':
    main()
