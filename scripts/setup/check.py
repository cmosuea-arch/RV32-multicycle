#!/usr/bin/env python3
"""Diagnóstico de ferramentas e teste real de suporte RV32I_Zmmul, sem tocar no RTL."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    failed = []
    print(f'Python: {sys.version.split()[0]} ({sys.executable})')
    if sys.version_info < (3, 9):
        failed.append('Python >= 3.9')
    commands = {
        'git': '--version', 'make': '--version', 'iverilog': '-V',
        'vvp': '-V', 'verilator': '--version', 'yosys': '-V',
        **{f'riscv64-unknown-elf-{tool}': '--version'
           for tool in ('gcc', 'objcopy', 'objdump', 'size')},
    }
    for name, flag in commands.items():
        path = shutil.which(name)
        if path is None:
            print(f'FALTA: {name}')
            failed.append(name)
            continue
        try:
            result = subprocess.run([path, flag], capture_output=True, text=True, timeout=15)
            output = (result.stdout + result.stderr).strip().splitlines()
            print(f'{name}: {output[0] if output else "sem versão"} [{path}]')
            if result.returncode:
                failed.append(name)
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f'ERRO: {name}: {error}')
            failed.append(name)
    if not failed:
        # Uma ferramenta com prefixo riscv64 também deve aceitar alvo e ABI RV32.
        with tempfile.TemporaryDirectory(prefix='cmos-toolchain-') as temp:
            obj = Path(temp) / 'probe.o'
            try:
                result = subprocess.run([
                    'riscv64-unknown-elf-gcc', '-march=rv32i_zmmul', '-mabi=ilp32',
                    '-ffreestanding', '-x', 'c', '-c', '-o', str(obj), '-'],
                    input='unsigned f(unsigned a,unsigned b) { return a*b; }\n',
                    capture_output=True, text=True, timeout=30)
                if result.returncode:
                    print(result.stderr)
                    failed.append('compilação RV32I_Zmmul/ILP32')
                else:
                    print('PASS: compilação RV32I_Zmmul/ILP32')
            except (OSError, subprocess.TimeoutExpired) as error:
                print(error)
                failed.append('compilação RV32I_Zmmul/ILP32')
    if failed:
        print('AMBIENTE INCOMPLETO: ' + ', '.join(failed))
        print('Execute bash scripts/setup/install.sh; confira também o PATH exibido.')
        return 1
    print('PASS: ambiente de simulação e firmware. Validação funcional: make regression.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
