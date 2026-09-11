#!/usr/bin/env python3
"""Write coverage only after a successful regression; official firmware separate."""
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/sim'))
from isa import CATEGORIES,fields


def write_coverage():
    enabled=set(json.loads((ROOT/'docs/isa/enabled.json').read_text()))
    counts=json.loads((ROOT/'build/isa_counts.json').read_text())
    if not enabled.issubset(counts):
        raise RuntimeError('coverage includes instructions absent from trace')
    headers=['Categoria','Instrução','Opcode','Funct3','Funct7','Módulo principal',
             'Teste unitário','Teste integrado','Regressão','Firmware oficial',
             'Commit','Evidência','Observação']
    modules={'Register':'alu','Immediate':'alu/imm_ext','Upper':'alu/pc/imm_ext',
             'Branch':'branch_comp','Jump':'pc/alu','Load':'lsu/dmem','Store':'lsu/dmem',
             'Multiplication':'multiplier','CRC':'PENDENTE','Sistema/Sincronização':'PENDENTE'}
    with (ROOT/'docs/isa/coverage.csv').open('w',newline='') as f:
        writer=csv.writer(f); writer.writerow(headers)
        for category,names in CATEGORIES.items():
            for name in names:
                op,f3,f7=fields(name)
                passed=name in enabled
                state='PASS' if passed else 'PENDENTE'
                writer.writerow([category,name,f'{op:07b}' if op is not None else '',
                                 f'{f3:03b}' if f3 is not None else '',f'{f7:07b}' if f7 is not None else '',
                                 modules[category],state,state,state,'PENDENTE',
                                 'ver git log -- rtl/decoder.sv' if passed else '',
                                 'results/logs/tb_decoder.log; results/logs/tb_isa.log' if passed else '',
                                 f'{counts.get(name,0)} aposentadorias no teste próprio' if passed else 'Definição oficial pendente'])
    lines=['# Cobertura ISA','',f'**{len(enabled)}/47 ({len(enabled)/47:.2%})** com testes unitários e execução no core.','',
           '| Categoria | Implementadas | Cobertura |','|---|---:|---:|']
    for category,names in CATEGORIES.items():
        n=len(enabled.intersection(names))
        lines.append(f'| {category} | {n}/{len(names)} | {n/len(names):.2%} |')
    lines += ['', 'Detalhes e codificações: [coverage.csv](coverage.csv).',
              'PASS representa os testes disponíveis, não prova formal nem certificação da competição.',
              'Firmware oficial ainda PENDENTE. Slots de sistema não são nomes de instruções.',
              'Cada tag incremental conserva os logs da respectiva regressão.']
    (ROOT/'docs/isa/coverage.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__': write_coverage()
