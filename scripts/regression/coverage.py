#!/usr/bin/env python3
"""Write coverage only after a successful regression; official firmware separate."""
import csv
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/sim'))
from isa import CATEGORIES,fields
from coverage_xlsx import generate_xlsx


def write_coverage():
    # Chamado pelo executor após sucesso; sozinho não executa nem certifica os TBs.
    enabled=set(json.loads((ROOT/'docs/isa/enabled.json').read_text()))
    counts=json.loads((ROOT/'build/isa_counts.json').read_text())
    if not enabled.issubset(counts):
        # Exige presença no trace modelado; a comparação desse trace é feita em tb_isa.
        raise RuntimeError('coverage includes instructions absent from trace')
    headers=['Categoria','Instrução','Opcode','Funct3','Funct7','Módulo principal',
             'Teste unitário','Teste integrado','Regressão','Firmware oficial',
             'Commit','Evidência','Observação']
    modules={'Register':'alu','Immediate':'alu/imm_ext','Upper':'alu/pc/imm_ext',
             'Branch':'branch_comp','Jump':'pc/alu','Load':'lsu/dmem','Store':'lsu/dmem',
             'Multiplication':'multiplier','CRC':'PENDENTE','Sistema/Sincronização':'PENDENTE'}
    unit_logs={'Register':'tb_alu','Immediate':'tb_imm_ext; tb_alu','Upper':'tb_imm_ext; tb_pc',
               'Branch':'tb_branch_comp','Jump':'tb_pc; tb_imm_ext','Load':'tb_lsu; tb_dmem',
               'Store':'tb_lsu; tb_dmem','Multiplication':'tb_multiplier'}
    with (ROOT/'docs/isa/coverage.csv').open('w',newline='') as f:
        writer=csv.writer(f,lineterminator='\n'); writer.writerow(headers)
        for category,names in CATEGORIES.items():
            for name in names:
                op,f3,f7=fields(name)
                passed=name in enabled
                state='PASS' if passed else 'PENDENTE'
                writer.writerow([category,name,f'{op:07b}' if op is not None else '',
                                 f'{f3:03b}' if f3 is not None else '',f'{f7:07b}' if f7 is not None else '',
                                 modules[category],state,state,state,'PENDENTE',
                                 'isa-41-v1' if passed else '',
                                 ('; '.join('results/logs/'+test+'.log' for test in
                                            ['tb_decoder',*unit_logs[category].split('; '),'tb_isa'])) if passed else '',
                                 f'{counts.get(name,0)} aposentadorias no teste próprio' if passed else 'Definição oficial pendente'])
    render_coverage()


def render_coverage():
    """Render the recorded CSV without rerunning tests or changing their results."""
    with (ROOT/'docs/isa/coverage.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    groups={}
    for row in rows:
        groups.setdefault(row['Categoria'],[]).append(row)
    labels={'Register':'Aritmética e lógica — registradores',
            'Immediate':'Aritmética e lógica — imediatos',
            'Upper':'Imediatos superiores','Branch':'Desvios condicionais',
            'Jump':'Saltos','Load':'Leitura de memória','Store':'Escrita de memória',
            'Multiplication':'Multiplicação — Zmmul','CRC':'CRC — Xicrc'}

    def passed(row):
        return all(row[field]=='PASS' for field in ('Teste unitário','Teste integrado','Regressão'))

    def percent(n,total):
        return f'{100*n/total:.2f}%'.replace('.',',') if total else '—'

    def code(value):
        return f'`{value}`' if value else '—'

    total=len(rows)
    n=sum(passed(row) for row in rows)
    lines=['# Cobertura ISA','',f'**{n}/{total} instruções ({percent(n,total)})** com testes unitários, integração e regressão PASS registrados.','',
           'Os estados abaixo são resultados preservados; uma nova validação exige executar `make regression`.',
           'Abra a [planilha Excel](coverage.xlsx) para filtrar, ordenar e consultar todos os campos.',
           'Esta página apresenta os mesmos resultados registrados em [coverage.csv](coverage.csv).',
           'As codificações abaixo estão em binário; **—** indica campo não aplicável ou ainda não definido.','',
           '## Resumo por categoria','',
           '| Categoria | Implementadas | Cobertura |','|---|---:|---:|']
    for category,items in groups.items():
        count=sum(passed(row) for row in items)
        lines.append(f'| {labels.get(category,category)} | {count}/{len(items)} | {percent(count,len(items))} |')
    lines.append(f'| **Total** | **{n}/{total}** | **{percent(n,total)}** |')
    firmware=', '.join(dict.fromkeys(row['Firmware oficial'] for row in rows))
    lines += ['',f'**Firmware oficial:** {firmware}. O firmware próprio não substitui essa validação.',
              'Slots de sistema são pendências, não nomes oficiais de instruções.']
    for category,items in groups.items():
        lines += ['',f'## {labels.get(category,category)}','']
        modules=list(dict.fromkeys(part for row in items for part in row['Módulo principal'].split('/')))
        module_links=[f'[{m}](../modules/{m}.md)' if m!='PENDENTE' else 'PENDENTE' for m in modules]
        commits=list(dict.fromkeys(row['Commit'] for row in items if row['Commit']))
        lines += ['**Módulos:** '+', '.join(module_links)+'.',
                  '**Commit/tag validado:** '+(', '.join(code(c) for c in commits) if commits else 'PENDENTE')+'.','',
                  '| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |',
                  '|---|---|---|---|---|---|---|---:|']
        for row in items:
            count=row['Observação'].split()[0] if row['Observação'] else ''
            executions=f'{int(count):,}'.replace(',','.') if count.isdigit() else '—'
            cells=[code(row['Instrução']),code(row['Opcode']),code(row['Funct3']),code(row['Funct7']),
                   row['Teste unitário'],row['Teste integrado'],row['Regressão'],executions]
            lines.append('| '+' | '.join(cells)+' |')
        evidence=list(dict.fromkeys(path for row in items for path in row['Evidência'].split('; ') if path))
        if evidence:
            lines += ['','**Evidências:** '+', '.join(f'[{Path(path).stem}](../../{path})' for path in evidence)+'.']
        notes=list(dict.fromkeys(row['Observação'] for row in items if row['Observação'] and not row['Observação'].split()[0].isdigit()))
        if notes:
            lines += ['','**Pendência:** '+'; '.join(notes)+'. Ver [definições oficiais necessárias](../architecture/official_questions.md).']
    # O CSV também pode apontar a evidências históricas após limpar o workspace.
    candidates=list(dict.fromkeys(str(Path(path).parent/'regression.json')
                    for row in rows for path in row['Evidência'].split('; ') if path))
    manifest=next((path for path in candidates if (ROOT/path).is_file()),None)
    manifest_note=(f'Manifesto preservado junto aos caminhos da matriz: [regression.json](../../{manifest}). '
                   'Confira a identificação da rodada antes de combinar logs de exercícios individuais.'
                   if manifest else 'O manifesto da nova rodada será publicado em `results/logs/regression.json` após a regressão.')
    lines += ['', '## Como interpretar','',
              '¹ Execuções são aposentadorias verificadas no teste próprio por instrução, incluindo instruções auxiliares que preparam operandos.',
              'PASS representa os testes disponíveis, não prova formal nem certificação da competição.',
              'A tag identifica o marco RTL; '+manifest_note,
              'Cada tag incremental conserva os logs da respectiva regressão. Esta tabela é atualizada automaticamente pela regressão.',
              'Para apenas reformatar os resultados existentes: `python3 scripts/regression/coverage.py --render-only`.']
    (ROOT/'docs/isa/coverage.md').write_text('\n'.join(lines)+'\n')
    generate_xlsx(ROOT/'docs/isa/coverage.csv', ROOT/'docs/isa/coverage.xlsx')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--render-only',action='store_true',help='format existing CSV without changing recorded results')
    args=parser.parse_args()
    if args.render_only:
        render_coverage()
    else:
        write_coverage()
