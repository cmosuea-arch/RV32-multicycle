#!/usr/bin/env python3
"""Write coverage only after a successful regression; official firmware separate."""
# CSV é a matriz rastreável; Markdown e XLSX são apresentações dos mesmos registros.
import csv
import argparse
import json
import hashlib
import subprocess
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/sim'))
from isa import CATEGORIES,fields,SYSTEM
from coverage_xlsx import generate_xlsx


def write_coverage(passed_tests):
    # Chamado pelo executor após sucesso; sozinho não executa nem certifica os TBs.
    enabled=set(json.loads((ROOT/'docs/isa/enabled.json').read_text()))
    counts=json.loads((ROOT/'build/isa_counts.json').read_text())
    official=json.loads((ROOT/'results/logs/official_firmware.json').read_text())
    system=json.loads((ROOT/'results/logs/system.json').read_text())
    required_tests={'tb_decoder','tb_control_unit','tb_core_system','tb_isa','tb_official_firmware'}
    if not required_tests.issubset(passed_tests):
        raise RuntimeError('missing current unit/integration/official coverage tests')
    revision=subprocess.run(['git','rev-parse','--short','HEAD'],cwd=ROOT,capture_output=True,text=True)
    commit='worktree / SHA-256 regression.json'
    if revision.returncode==0:
        changes=subprocess.run(['git','status','--porcelain','--','rtl','tb','scripts',
                                'firmware','Makefile','docs/isa/enabled.json'],
                               cwd=ROOT,capture_output=True,text=True,check=True)
        commit=revision.stdout.strip()+(' + worktree' if changes.stdout.strip() else '')
    system_names=set(CATEGORIES['Sistema/Sincronização'])
    # A implementação tem 47 tipos, mas a imagem oficial só exercita os outros 44.
    if official.get('status')!='PASS' or set(official.get('instructions',[]))!=enabled-system_names:
        raise RuntimeError('official firmware execution does not cover its published 44-type inventory')
    if system.get('status')!='PASS' or system.get('trap_instructions_retired')!=0 or any(
            system.get('checks',{}).get(name,0)<=0 for name in system_names):
        raise RuntimeError('missing precise system/trap evidence')
    for proof in (official,system):
        # Alterar até um comentário muda o hash: os logs antigos continuam históricos.
        if not proof.get('sha256'):
            raise RuntimeError('missing coverage evidence hashes')
        for name,expected in proof['sha256'].items():
            if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
                raise RuntimeError(f'stale coverage evidence: {name}')
    if not (enabled-set(SYSTEM)).issubset(counts) or any(counts.get(name,0)<=0 for name in enabled-set(SYSTEM)):
        # Exige presença no trace modelado; a comparação desse trace é feita em tb_isa.
        raise RuntimeError('coverage includes instructions absent from trace')
    # ECALL/EBREAK são eventos de trap; FENCE deve constar no trace de aposentadorias.
    if set(SYSTEM).intersection(counts):
        raise RuntimeError('trap instructions must not be counted as retirements')
    # Relaciona cada grupo da ISA a módulos e logs que sustentam seus estados.
    headers=['Categoria','Instrução','Opcode','Funct3','Funct7','Módulo principal',
             'Teste unitário','Teste integrado','Regressão','Firmware oficial',
             'Commit','Evidência','Observação']
    modules={'Register':'alu','Immediate':'alu/imm_ext','Upper':'alu/pc/imm_ext',
             'Branch':'branch_comp','Jump':'pc/alu','Load':'lsu/dmem','Store':'lsu/dmem',
             'Multiplication':'multiplier','CRC':'crc','Sistema/Sincronização':'decoder/control_unit/riscv_core'}
    unit_logs={'Register':'tb_alu','Immediate':'tb_imm_ext; tb_alu','Upper':'tb_imm_ext; tb_pc',
               'Branch':'tb_branch_comp','Jump':'tb_pc; tb_imm_ext','Load':'tb_lsu; tb_dmem',
               'Store':'tb_lsu; tb_dmem','Multiplication':'tb_multiplier','CRC':'tb_crc',
               'Sistema/Sincronização':'tb_decoder; tb_control_unit'}
    with (ROOT/'docs/isa/coverage.csv').open('w',newline='') as f:
        writer=csv.writer(f,lineterminator='\n'); writer.writerow(headers)
        for category,names in CATEGORIES.items():
            for name in names:
                op,f3,f7=fields(name)
                # Traps têm evidência própria e não são aposentadorias do trace.
                passed=name in enabled
                state='PASS' if passed else 'PENDENTE'
                is_system=name in system_names
                observations=(f'{system["checks"][name]} traps precisos verificados; não aposenta' if name in SYSTEM
                              else f'{counts.get(name,0)} aposentadorias no teste próprio')
                if is_system:
                    observations+='; contrato EEI CMOS, firmware publicado não exercita'
                tests=list(dict.fromkeys(['tb_decoder',*unit_logs[category].split('; '),
                    *(['tb_core_system'] if is_system else []),
                    *([] if name in SYSTEM else ['tb_isa']),
                    *([] if is_system else ['tb_official_firmware'])]))
                # Não atribui PASS oficial a instruções ausentes da imagem publicada.
                writer.writerow([category,name,f'{op:07b}' if op is not None else '',
                                 f'{f3:03b}' if f3 is not None else '',f'{f7:07b}' if f7 is not None else '',
                                 modules[category],state,state,state,'NÃO EXERCITADA' if is_system else state,
                                 commit if passed else '',
                                 '; '.join('results/logs/'+test+'.log' for test in tests) if passed else '',
                                 observations if passed else 'Implementação pendente'])
    render_coverage()


def render_coverage():
    """Render the recorded CSV without rerunning tests or changing their results."""
    with (ROOT/'docs/isa/coverage.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    # Agrupa as linhas para gerar resumo percentual e tabelas por categoria.
    groups={}
    for row in rows:
        groups.setdefault(row['Categoria'],[]).append(row)
    labels={'Register':'Aritmética e lógica — registradores',
            'Immediate':'Aritmética e lógica — imediatos',
            'Upper':'Imediatos superiores','Branch':'Desvios condicionais',
            'Jump':'Saltos','Load':'Leitura de memória','Store':'Escrita de memória',
            'Multiplication':'Multiplicação — Zmmul','CRC':'CRC — Xicrc'}

    def passed(row):
        # Conta como implementada somente se os três níveis de teste estão PASS.
        return all(row[field]=='PASS' for field in ('Teste unitário','Teste integrado','Regressão'))

    def percent(n,total):
        # Formata o percentual para leitura em português, sem alterar a contagem.
        return f'{100*n/total:.2f}%'.replace('.',',') if total else '—'

    def code(value):
        # Campos vazios viram travessão; codificações presentes usam fonte de código.
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
    # Primeiro o resumo; depois as tabelas detalhadas com módulos, logs e pendências.
    for category,items in groups.items():
        count=sum(passed(row) for row in items)
        lines.append(f'| {labels.get(category,category)} | {count}/{len(items)} | {percent(count,len(items))} |')
    lines.append(f'| **Total** | **{n}/{total}** | **{percent(n,total)}** |')
    firmware=', '.join(dict.fromkeys(row['Firmware oficial'] for row in rows))
    lines += ['',f'**Firmware oficial:** {firmware}. A evidência da execução fica em `official_firmware.json` junto aos logs.',
              'O firmware publicado exercita 44 tipos; FENCE/ECALL/EBREAK têm testes próprios sob o [contrato EEI CMOS](../architecture/system.md).']
    for category,items in groups.items():
        lines += ['',f'## {labels.get(category,category)}','']
        modules=list(dict.fromkeys(part for row in items for part in row['Módulo principal'].split('/')))
        module_links=[f'[{m}](../modules/{m}.md)' if m!='PENDENTE' else 'PENDENTE' for m in modules]
        commits=list(dict.fromkeys(row['Commit'] for row in items if row['Commit']))
        lines += ['**Módulos:** '+', '.join(module_links)+'.',
                  '**Commit/tag validado:** '+(', '.join(code(c) for c in commits) if commits else 'PENDENTE')+'.','',
                  '| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Eventos¹ |',
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
            lines += ['','**Observações:** '+'; '.join(notes)+'. Ver [contratos e questões oficiais](../architecture/official_questions.md).']
    # O CSV também pode apontar a evidências históricas após limpar o workspace.
    candidates=list(dict.fromkeys(str(Path(path).parent/'regression.json')
                    for row in rows for path in row['Evidência'].split('; ') if path))
    manifest=next((path for path in candidates if (ROOT/path).is_file()),None)
    manifest_note=(f'Manifesto preservado junto aos caminhos da matriz: [regression.json](../../{manifest}). '
                   'Confira a identificação da rodada antes de combinar logs de exercícios individuais.'
                   if manifest else 'O manifesto da nova rodada será publicado em `results/logs/regression.json` após a regressão.')
    lines += ['', '## Como interpretar','',
              '¹ Eventos são aposentadorias do trace próprio; para ECALL/EBREAK são traps precisos verificados, sem aposentadoria. Incluem instruções auxiliares que preparam operandos.',
              'PASS representa os testes disponíveis, não prova formal nem certificação da competição.',
              'A tag identifica o marco RTL; '+manifest_note,
              'Cada tag incremental conserva os logs da respectiva regressão. Esta tabela é atualizada automaticamente pela regressão.',
              'Para apenas reformatar os resultados existentes: `python3 scripts/regression/coverage.py --render-only`.']
    (ROOT/'docs/isa/coverage.md').write_text('\n'.join(lines)+'\n')
    generate_xlsx(ROOT/'docs/isa/coverage.csv', ROOT/'docs/isa/coverage.xlsx')


if __name__=='__main__':
    # --render-only preserva o CSV e só refaz suas apresentações Markdown/Excel.
    parser=argparse.ArgumentParser()
    parser.add_argument('--render-only',action='store_true',help='format existing CSV without changing recorded results')
    args=parser.parse_args()
    if args.render_only:
        render_coverage()
    else:
        raise SystemExit('A publicação exige a rodada completa: execute make regression.')
