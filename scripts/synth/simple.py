#!/usr/bin/env python3
"""Síntese lógica genérica e teste da netlist; não executa fluxo físico/GDSII."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def run(args,log):
    try:
        p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=180)
    except subprocess.TimeoutExpired as error:
        log.write_text('TIMEOUT: '+' '.join(args)+'\n')
        raise RuntimeError(f'timeout: {log}') from error
    log.write_text('$ '+' '.join(args)+'\n'+p.stdout+p.stderr)
    if p.returncode:
        raise RuntimeError(f'command failed: see {log}')
    return p.stdout+p.stderr


def main():
    logs=ROOT/'results/logs'
    logs.mkdir(parents=True,exist_ok=True)
    for tool in ('yosys','iverilog','vvp'):
        if not shutil.which(tool):
            raise RuntimeError(f'{tool} ausente; execute scripts/setup/install.sh')
    if not (ROOT/'build/simple.hex').is_file():
        raise RuntimeError('execute make simple-firmware primeiro')
    rtl=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'rtl').glob('*.sv'))
    flow='; '.join([
        'read_verilog -sv -defer '+' '.join(rtl),
        'hierarchy -check -top simple_system',
        'synth -top simple_system -flatten',
        'check -assert', 'stat',
        'write_verilog -noattr build/simple_netlist.v',
        'write_json build/simple_netlist.json'])
    run(['yosys','-p',flow],logs/'simple_synth.log')
    top=json.loads((ROOT/'build/simple_netlist.json').read_text())['modules']['simple_system']
    cells=top.get('cells',{})
    if top.get('memories') or any('$mem' in c['type'] for c in cells.values()):
        raise RuntimeError('memória não mapeada na netlist')
    if any('init' in net.get('attributes',{}) for net in top['netnames'].values()):
        raise RuntimeError('netlist depende de inicialização de registrador')
    counts={}
    for cell in cells.values():
        counts[cell['type']]=counts.get(cell['type'],0)+1
    if not any('DFF' in kind for kind in counts):
        raise RuntimeError('circuito sequencial ausente')
    for name in ('done_o','success_o','fault_o'):
        if not all(isinstance(bit,int) for bit in top['ports'][name]['bits']):
            raise RuntimeError(f'saída constante inesperada: {name}')
    run(['iverilog','-g2012','-s','tb_simple_netlist','-o','build/tb_simple_netlist',
         'build/simple_netlist.v','scripts/synth/tb_simple_netlist.sv'],logs/'simple_netlist.compile.log')
    output=run(['vvp','build/tb_simple_netlist'],logs/'simple_netlist.log')
    if 'PASS' not in output:
        raise RuntimeError('netlist sem PASS')
    version=run(['yosys','-V'],logs/'yosys_version.log').strip()
    files=rtl+['build/simple.hex','build/simple_netlist.v','scripts/synth/simple.py','scripts/synth/tb_simple_netlist.sv']
    summary={'status':'PASS','scope':'generic synthesis; no PDK/timing/physical signoff',
             'yosys':version,'cells':len(cells),'cell_types':counts,'netlist_simulation':'PASS',
             'sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}}
    (logs/'simple_synth.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(output.strip())
    print(f'PASS simple synthesis: {len(cells)} generic cells, mapped memories, no register init')


if __name__=='__main__':
    try:
        main()
    except (RuntimeError,OSError) as error:
        # Uma execução falha não deixa manifesto PASS antigo para esta etapa.
        path=ROOT/'results/logs/simple_synth.json'
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'status':'FAIL','error':str(error)},indent=2)+'\n')
        sys.exit(str(error))
