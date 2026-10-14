#!/usr/bin/env python3
"""Compila o firmware do simple_system e verifica os limites físicos da ROM."""
from build_firmware import ROOT, BUILD, LOGS, command


def main():
    BUILD.mkdir(exist_ok=True)
    LOGS.mkdir(parents=True,exist_ok=True)
    prefix='riscv64-unknown-elf-'
    args=[prefix+'gcc','-march=rv32i_zmmul','-mabi=ilp32','-Os','-g',
          '-ffreestanding','-fno-builtin','-fno-pic','-msmall-data-limit=0',
          '-fno-strict-aliasing','-Wall','-Wextra','-Werror','-nostdlib','-nostartfiles',
          '-Wl,--no-relax,-T,firmware/simple/link.ld,-Map,build/simple.map',
          'firmware/simple/start.S','firmware/simple/main.c','-o','build/simple.elf']
    command(args)
    command([prefix+'objcopy','-O','binary','build/simple.elf','build/simple.bin'])
    data=(BUILD/'simple.bin').read_bytes()
    size=len(data)
    if size>2048:
        raise RuntimeError('simple ROM exceeds 2 KiB')
    data+=bytes(2048-size)
    (BUILD/'simple.hex').write_text(''.join(f'{int.from_bytes(data[i:i+4],"little"):08x}\n' for i in range(0,len(data),4)))
    (LOGS/'simple.disasm').write_text(command([prefix+'objdump','-d','-M','no-aliases','build/simple.elf']))
    (LOGS/'simple_build.log').write_text('$ '+' '.join(args)+'\n'+command([prefix+'size','build/simple.elf'])+f'ROM image: {size}/2048 bytes\n')
    print(f'PASS simple firmware: {size}/2048 ROM bytes, 1 KiB RAM, provisional CRC enabled')


if __name__=='__main__': main()
