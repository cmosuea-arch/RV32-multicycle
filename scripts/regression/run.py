#!/usr/bin/env python3
"""Run existing self-checking testbenches and retain reproducible logs."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def run(cmd, log):
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    log.write_text('$ ' + ' '.join(map(str, cmd)) + '\n' + result.stdout)
    if result.returncode:
        print(result.stdout)
        raise RuntimeError(f'command failed: {cmd[0]} (see {log})')
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lint-only', action='store_true')
    args = parser.parse_args()
    build, logs = ROOT / 'build', ROOT / 'results/logs'
    build.mkdir(exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    rtl = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'rtl').glob('*.sv'))
    if args.lint_only:
        if not rtl:
            raise RuntimeError('no RTL to lint')
        run(['verilator', '--lint-only', '-Wall', '-Wno-DECLFILENAME',
             '-Wno-UNUSEDSIGNAL', '-Wno-UNUSEDPARAM', '-Wno-MULTITOP',
             *rtl], logs / 'lint.log')
        print('PASS lint (Verilator)')
        return
    generator = ROOT / 'scripts/sim/vectors.py'
    if generator.exists():
        run([sys.executable, str(generator)], logs / 'vectors.log')
    benches = sorted((ROOT / 'tb').glob('**/tb_*.sv'))
    if not benches:
        raise RuntimeError('no tests discovered')
    for tb in benches:
        name = tb.stem
        exe = build / name
        diagnostics = run(['iverilog', '-g2012', '-Wall', '-s', name, '-o', str(exe),
                           *rtl, str(tb)], logs / f'{name}.compile.log')
        if diagnostics.strip():
            raise RuntimeError(f'{name}: compilation diagnostics: {diagnostics}')
        output = run(['vvp', str(exe)], logs / f'{name}.log')
        if 'PASS' not in output:
            raise RuntimeError(f'{name}: missing PASS marker')
        print('\n'.join(line for line in output.splitlines() if 'PASS' in line))
    print(f'PASS regression: {len(benches)} testbenches')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError) as error:
        sys.exit(str(error))
