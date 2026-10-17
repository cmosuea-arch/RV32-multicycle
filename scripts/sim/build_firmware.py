#!/usr/bin/env python3
"""Build the own RV32I_Zmmul demo and a padded word ROM image."""
# Caminho: start.S + main.c + link.ld -> ELF -> binário -> smoke.hex lido pela IMEM.
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'build'
LOGS=ROOT/'results/logs'


def command(args):
    # Executa a ferramenta na raiz; erro ou diagnóstico em stderr interrompe o build.
    p=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if p.returncode or p.stderr:
        raise RuntimeError(' '.join(args)+'\n'+p.stdout+p.stderr)
    return p.stdout


def main():
    BUILD.mkdir(exist_ok=True); LOGS.mkdir(parents=True,exist_ok=True)
    # Referência independente do checksum que o programa C deve calcular no core.
    expected=0
    for i in range(16):
        x,y=i+1,0x10203+i
        expected ^= (x*y+((x<<5)^(y>>3)))&0xffffffff
    prefix='riscv64-unknown-elf-'
    # O prefixo da ferramenta é riscv64, mas -march/-mabi selecionam RV32 de 32 bits.
    # Sem biblioteca/startup do sistema: start.S e link.ld definem o boot e as regiões.
    # --no-relax mantém sequências de endereço sem depender de um global pointer.
    args=[prefix+'gcc','-march=rv32i_zmmul','-mabi=ilp32','-O2','-g',
          '-ffreestanding','-fno-builtin','-fno-pic','-msmall-data-limit=0',
          '-fno-strict-aliasing','-Wall','-Wextra','-Werror','-nostdlib','-nostartfiles',
          '-Wl,--no-relax,-T,firmware/smoke/link.ld,-Map,build/smoke.map',
          f'-DEXPECTED_SUM=0x{expected:08x}u','firmware/smoke/start.S','firmware/smoke/main.c',
          '-o','build/smoke.elf']
    command(args)
    # ELF tem símbolos/seções; objcopy extrai os bytes que formarão a imagem da ROM.
    command([prefix+'objcopy','-O','binary','build/smoke.elf','build/smoke.bin'])
    data=(BUILD/'smoke.bin').read_bytes()
    # Gera palavras little-endian para a ROM de 4096 palavras do tb_firmware.
    if len(data)>16384: raise RuntimeError('smoke ROM exceeds configured size')
    data+=bytes(16384-len(data))
    (BUILD/'smoke.hex').write_text(''.join(f'{int.from_bytes(data[i:i+4],"little"):08x}\n' for i in range(0,len(data),4)))
    # Disassembly liga endereços/instruções à waveform; o log registra comando e tamanho.
    disassembly=command([prefix+'objdump','-d','-M','no-aliases','build/smoke.elf'])
    (LOGS/'smoke.disasm').write_text(disassembly)
    (LOGS/'firmware_build.log').write_text('$ '+' '.join(args)+'\n'+command([prefix+'size','build/smoke.elf'])+f'Expected checksum: 0x{expected:08x}\n')
    print(f'PASS own firmware built: RV32I_Zmmul, checksum 0x{expected:08x}')


if __name__=='__main__': main()
