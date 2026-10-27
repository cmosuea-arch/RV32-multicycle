#!/usr/bin/env python3
"""Run existing self-checking testbenches and retain reproducible logs."""
# O Makefile escolhe o modo; este executor prepara entradas, compila, simula e registra.
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def run(cmd, log):
    # Mantém o diretório e os logs previsíveis; erro ou timeout interrompem o fluxo.
    try:
        result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=120)
    except subprocess.TimeoutExpired as error:
        log.write_text('$ ' + ' '.join(map(str, cmd)) + '\nTIMEOUT after 120 seconds\n')
        raise RuntimeError(f'command timeout (see {log})') from error
    log.write_text('$ ' + ' '.join(map(str, cmd)) + '\n' + result.stdout)
    if result.returncode:
        print(result.stdout)
        raise RuntimeError(f'command failed: {cmd[0]} (see {log})')
    return result.stdout


def lint(rtl, logs):
    # Analisa o RTL sem simular estímulos; diagnósticos também reprovam a checagem.
    if not rtl:
        raise RuntimeError('no RTL to lint')
    # Elabora separadamente as duas configurações reais de parâmetros/memórias.
    # Todos os blocos estão conectados em pelo menos um destes tops (incluindo CRC).
    combined=[]
    for top in ('riscv_top','simple_system'):
        log=logs / f'lint_{top}.log'
        diagnostics = run(['verilator', '--lint-only', '-Wall', '-Wno-DECLFILENAME',
                          '-Wno-UNUSEDSIGNAL', '-Wno-UNUSEDPARAM', '--top-module',top,
                          *rtl], log)
        combined.append(log.read_text())
        (logs/'lint.log').write_text('\n'.join(combined))
        if diagnostics.strip():
            raise RuntimeError(f'lint diagnostics: {diagnostics}')
    print('PASS lint (Verilator): riscv_top + simple_system')


def main():
    # Os modos selecionam uma bancada, uma suíte ou todos os testes disponíveis.
    # Modos são exclusivos; --with-lint pode acompanhar uma execução de testes.
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--lint-only', action='store_true')
    mode.add_argument('--smoke', action='store_true')
    mode.add_argument('--wave', action='store_true')
    mode.add_argument('--suite', choices=('unit', 'integration'))
    mode.add_argument('--test', metavar='TB_NAME')
    parser.add_argument('--with-lint', action='store_true')
    parser.add_argument('--with-wave', action='store_true', help='grava VCD ao selecionar tb_firmware ou tb_official_firmware')
    args = parser.parse_args()
    selected_test = args.test.removesuffix('.sv') if args.test else None
    if args.with_wave and selected_test not in ('tb_firmware', 'tb_official_firmware'):
        parser.error('--with-wave exige --test tb_firmware ou tb_official_firmware')
    dump_wave = args.wave or args.with_wave
    build, logs = ROOT / 'build', ROOT / 'results/logs'
    build.mkdir(exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    rtl = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'rtl').glob('*.sv'))
    if args.lint_only:
        lint(rtl, logs)
        return
    full = not (args.smoke or args.wave or args.suite or args.test)
    # Só uma execução completa publica o manifesto agregado e a matriz de ISA.
    if full:
        (logs / 'regression.json').write_text(json.dumps({'status': 'RUNNING'}) + '\n')
    generator = ROOT / 'scripts/sim/vectors.py'
    # Recria entradas antes da simulação para evitar dependência de build/ antigo.
    if not args.wave and generator.exists():
        run([sys.executable, str(generator)], logs / 'vectors.log')
        run([sys.executable, str(ROOT/'scripts/sim/crc_vectors.py')], logs / 'crc_vectors.log')
    programs = ROOT / 'scripts/sim/programs.py'
    if (full or args.suite in ('unit','integration') or args.test) and programs.exists():
        run([sys.executable, str(programs)], logs / 'programs.log')
    firmware = ROOT / 'scripts/sim/build_firmware.py'
    # GCC só é necessário nos modos que incluem uma bancada de firmware.
    needs_firmware = full or args.wave or args.suite == 'integration' or selected_test == 'tb_firmware'
    if needs_firmware and firmware.exists():
        run([sys.executable, str(firmware)], logs / 'firmware.log')
    if full or args.suite == 'integration' or selected_test == 'tb_simple_system':
        run([sys.executable, str(ROOT/'scripts/sim/build_simple.py')], logs / 'simple_firmware.log')
    needs_official = full or args.suite == 'integration' or selected_test == 'tb_official_firmware'
    if needs_official:
        # A cópia original é obtida explicitamente por make official-fetch, fora da regressão.
        (logs/'official_firmware.json').write_text(json.dumps({'status': 'RUNNING'})+'\n')
        run([sys.executable, str(ROOT/'scripts/sim/build_official.py')], logs/'official_image.log')
    needs_system = full or args.suite == 'integration' or selected_test == 'tb_core_system'
    if needs_system:
        (logs/'system.json').write_text(json.dumps({'status':'RUNNING'})+'\n')
    benches = sorted((ROOT / 'tb').glob('**/tb_*.sv'))
    # A descoberta é alfabética; a ordem didática está no laboratório.
    if args.smoke:
        names = {'tb_core_smoke', 'tb_branch_pc', 'tb_lsu_dmem', 'tb_mult_rf'}
        benches = [p for p in benches if p.stem in names]
        if len(benches) != len(names):
            raise RuntimeError('missing smoke bench')
    elif args.wave:
        benches = [p for p in benches if p.stem == 'tb_firmware']
        (ROOT / 'results/waveforms').mkdir(parents=True, exist_ok=True)
    elif args.suite:
        benches = [p for p in benches if p.parent.name == args.suite]
    elif args.test:
        benches = [p for p in benches if p.stem == selected_test]
        if len(benches) != 1:
            raise RuntimeError(f'unknown or ambiguous testbench: {args.test}')
    if not benches:
        raise RuntimeError('no tests discovered')
    if dump_wave:
        (ROOT/'results/waveforms').mkdir(parents=True, exist_ok=True)
    passed = []
    for tb in benches:
        # -s escolhe o top; vvp executa somente a simulação elaborada para ele.
        name = tb.stem
        exe = build / name
        # iverilog elabora o circuito em um executável de simulação, não em hardware.
        diagnostics = run(['iverilog', '-g2012', '-Wall', '-s', name, '-o', str(exe),
                           *rtl, str(tb)], logs / f'{name}.compile.log')
        if diagnostics.strip():
            raise RuntimeError(f'{name}: compilation diagnostics: {diagnostics}')
        # vvp avança o tempo simulado; o TB compara resultados e pode encerrar com erro.
        output = run(['vvp', str(exe), *(['+WAVE'] if dump_wave else [])],
                     logs / (f'{name}.wave.log' if dump_wave else f'{name}.log'))
        if 'PASS' not in output:
            raise RuntimeError(f'{name}: missing PASS marker')
        print('\n'.join(line for line in output.splitlines() if 'PASS' in line))
        passed.append(name)
        if name == 'tb_core_system':
            line=next(line for line in output.splitlines() if line.startswith('PASS core_system:'))
            match=re.search(r'FENCE=(\d+) ECALL=(\d+) EBREAK=(\d+),',line)
            if not match or any(int(n)!=expected for n,expected in zip(match.groups(),(512,256,256))):
                raise RuntimeError('incomplete system checks')
            files=[*rtl,str(tb.relative_to(ROOT)),'scripts/sim/isa.py','scripts/sim/programs.py']
            proof={'status':'PASS','scope':'CMOS EEI: ordered FENCE and terminal requested traps; not privileged architecture',
                   'utc':datetime.now(timezone.utc).isoformat(),
                   'checks':dict(zip(('FENCE','ECALL','EBREAK'),map(int,match.groups()))),
                   'trap_instructions_retired':0,'result':line,
                   'sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}}
            (logs/'system.json').write_text(json.dumps(proof,indent=2)+'\n')
        if name == 'tb_official_firmware':
            image = json.loads((build/'official_image.json').read_text())
            files = [*rtl, str(tb.relative_to(ROOT)), 'scripts/sim/build_official.py',
                     'firmware/official/source.json', 'scripts/sim/isa.py',
                     'docs/isa/enabled.json', 'build/official.hex',
                     'build/official_tags.hex', 'build/official_meta.hex']
            proof = {'status': 'PASS', 'scope': 'official firmware RTL simulation; no physical signoff',
                     'utc': datetime.now(timezone.utc).isoformat(),
                     'source_commit': image['commit'], 'source_sha256': image['source_sha256'],
                     'instructions': image['instruction_order'],
                     'result': next(line for line in output.splitlines() if 'PASS official_firmware:' in line),
                     'sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}}
            (logs/'official_firmware.json').write_text(json.dumps(proof, indent=2)+'\n')
    if args.with_lint:
        lint(rtl, logs)
    print(f'PASS regression: {len(benches)} testbenches')
    if full and (ROOT / 'scripts/regression/coverage.py').exists():
        # Os hashes identificam o conteúdo verificado, inclusive scripts e firmware.
        from coverage import write_coverage
        write_coverage(passed)
        files = [ROOT / 'docs/isa/enabled.json', ROOT / 'Makefile']
        for folder in ('rtl', 'tb', 'scripts', 'firmware'):
            files += [p for p in (ROOT / folder).rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts]
        # Firmware oficial só recebe PASS quando sua bancada terminou nesta mesma rodada.
        manifest = {
            'status': 'PASS', 'utc': datetime.now(timezone.utc).isoformat(),
            'testbenches': passed, 'lint': 'PASS' if args.with_lint else 'NOT_RUN',
            'official_firmware': 'PASS' if 'tb_official_firmware' in passed else 'PENDING',
            'system': 'PASS' if 'tb_core_system' in passed else 'PENDING',
            'official_firmware_coverage': '44/47; FENCE/ECALL/EBREAK not exercised by published image',
            'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted(files)},
        }
        manifest['coverage'] = f"{len(json.loads((ROOT/'docs/isa/enabled.json').read_text()))}/47"
        (logs / 'regression.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    try:
        main()
    # Propaga a falha ao Make e invalida um manifesto que ainda estava em RUNNING.
    except (RuntimeError, OSError) as error:
        summary = ROOT / 'results/logs/regression.json'
        if summary.exists() and json.loads(summary.read_text()).get('status') == 'RUNNING':
            summary.write_text(json.dumps({'status': 'FAIL', 'error': str(error)}, indent=2) + '\n')
        official = ROOT/'results/logs/official_firmware.json'
        if official.exists() and json.loads(official.read_text()).get('status') == 'RUNNING':
            official.write_text(json.dumps({'status': 'FAIL', 'error': str(error)}, indent=2)+'\n')
        system = ROOT/'results/logs/system.json'
        if system.exists() and json.loads(system.read_text()).get('status') == 'RUNNING':
            system.write_text(json.dumps({'status':'FAIL','error':str(error)},indent=2)+'\n')
        sys.exit(str(error))
