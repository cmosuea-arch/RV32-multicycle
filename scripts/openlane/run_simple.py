#!/usr/bin/env python3
"""Executa o simple_system experimental em entradas congeladas no Docker."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path('openlane/simple_system/config.json')
MOUNT = Path('/home/designer/shared/cmos-riscv')
STAGES = {'synth': 'Checker.NetlistAssignStatements',
          'floorplan': 'OpenROAD.Floorplan', 'full': None}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    # Exige a síntese genérica e os dois boots da MESMA ROM/RTL antes de mapear no PDK.
    proof_path = ROOT / 'results/logs/simple_synth.json'
    if not proof_path.is_file():
        raise RuntimeError('Execute make simple-synth antes de iniciar o fluxo físico.')
    proof = json.loads(proof_path.read_text())
    if proof.get('status') != 'PASS' or proof.get('netlist_simulation') != 'PASS':
        raise RuntimeError('A síntese genérica/netlist anterior não possui PASS.')
    if not isinstance(proof.get('sha256'), dict) or not proof['sha256']:
        raise RuntimeError('Manifesto genérico incompleto; execute make simple-synth.')
    for name, expected in proof['sha256'].items():
        path = ROOT / name
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f'Evidência desatualizada: {name}; execute make simple-synth.')
    config = json.loads((ROOT / CONFIG).read_text())
    # Copia apenas os arquivos usados. O run não depende de edições posteriores no RTL.
    sources = [CONFIG, Path('build/simple.hex')]
    for key in ('VERILOG_FILES', 'PNR_SDC_FILE', 'SIGNOFF_SDC_FILE'):
        values = config[key] if isinstance(config[key], list) else [config[key]]
        for value in values:
            if not value.startswith('dir::'):
                raise RuntimeError(f'{key}: esperado caminho dir:: relativo ao projeto')
            name = Path(value.removeprefix('dir::'))
            if name.is_absolute() or '..' in name.parts:
                raise RuntimeError(f'Caminho fora do projeto: {name}')
            sources.append(name)
    required = {'build/simple.hex', *(str(name) for name in sources if name.suffix == '.sv')}
    if not required.issubset(proof.get('sha256', {})):
        raise RuntimeError('Manifesto genérico incompleto; execute make simple-synth.')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    work = ROOT / 'build/openlane-simple' / stamp
    design = work / 'design'
    design.mkdir(parents=True)
    hashes = {}
    for name in dict.fromkeys(sources):
        destination = design / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
        hashes[str(name)] = sha256(destination)
        if str(name) in proof['sha256'] and hashes[str(name)] != proof['sha256'][str(name)]:
            raise RuntimeError(f'Fonte mudou durante a cópia: {name}')
    # O Yosys roda em outro diretório: a ROM usa um caminho absoluto DENTRO da montagem.
    container_design = MOUNT / design.relative_to(ROOT)
    config['SYNTH_PARAMETERS'] = [f'ROM_FILE="{container_design / "build/simple.hex"}"']
    (design / CONFIG).write_text(json.dumps(config, indent=2) + '\n')
    return work, container_design, hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=STAGES, default='synth')
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs deve ser positivo')
    logs = ROOT / 'results/logs'
    logs.mkdir(parents=True, exist_ok=True)
    report_path = logs / 'simple_openlane.json'
    summary = {'status': 'RUNNING', 'scope': 'experimental simple_system; own firmware; provisional CRC',
               'stage_requested': args.stage, 'stop_after': STAGES[args.stage],
               'utc': datetime.now(timezone.utc).isoformat(),
               'responsible': os.environ.get('USER', 'unknown'),
               'image': os.environ.get('UNICCASS_DOCKER_IMAGE', 'isaiassh/unic-cass-tools:1.1.0'),
               'pdk': 'sky130A',
               'signoff_complete': False}
    work = None
    try:
        report_path.write_text(json.dumps(summary, indent=2) + '\n')
        work, design, hashes = prepare()
        summary.update(work=str(work.relative_to(ROOT)), source_sha256=hashes,
                       resolved_config_sha256=sha256(work / 'design' / CONFIG))
        commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                capture_output=True, text=True)
        summary['base_commit'] = commit.stdout.strip() if commit.returncode == 0 else None
        summary['driver_sha256'] = {
            name: sha256(ROOT / name) for name in
            ('Makefile', 'scripts/openlane/run_simple.py',
             'scripts/openlane/environment.sh', 'scripts/openlane/librelane.sh')}
        image = subprocess.run(['docker', 'image', 'inspect', summary['image'],
                                '--format', '{{.Id}}'], capture_output=True, text=True)
        summary['image_id'] = image.stdout.strip() if image.returncode == 0 else None
        command = ['bash', str(ROOT / 'scripts/openlane/environment.sh'), 'flow',
                   '--design-dir', str(design), '--run-tag', 'run', '--jobs', str(args.jobs),
                   '--hide-progress-bar', '--log-level', 'INFO']
        if STAGES[args.stage]:
            command += ['--to', STAGES[args.stage]]
        command += [str(design / CONFIG)]
        summary['command'] = command
        report_path.write_text(json.dumps(summary, indent=2) + '\n')
        print(f'Entradas e resultados isolados: {work.relative_to(ROOT)}', flush=True)
        # Mantém a saída visível no terminal e um log completo no diretório do run.
        with (work / 'console.log').open('w') as output:
            process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                print(line, end='', flush=True)
                output.write(line)
                output.flush()
            if process.wait():
                raise RuntimeError(f'LibreLane falhou; consulte {work.relative_to(ROOT)}/console.log')
        final = work / 'design/runs/run/final/metrics.json'
        summary['metrics'] = json.loads(final.read_text()) if final.is_file() else {}
        summary['status'] = 'PASS'
        print(f'PASS fluxo experimental: etapa {args.stage}; confira métricas e limites do run.')
    except (OSError, RuntimeError, ValueError) as error:
        summary.update(status='FAIL', error=str(error))
        raise
    except KeyboardInterrupt:
        summary.update(status='INTERRUPTED', error='Execução interrompida pelo usuário.')
        raise
    finally:
        # Um PASS parcial é sempre identificado pela etapa, sem declarar signoff final.
        content = json.dumps(summary, indent=2) + '\n'
        report_path.write_text(content)
        if work is not None:
            (work / 'summary.json').write_text(content)


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, ValueError) as error:
        sys.exit(str(error))
