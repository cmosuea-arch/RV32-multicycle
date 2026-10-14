#!/usr/bin/env python3
"""Vetores e programa CRC separados da cobertura oficial de 41 instruções."""
import random
from crc_model import crc_model, check_reference
from programs import Program
from vectors import OUT, EDGES


def main():
    OUT.mkdir(exist_ok=True)
    check_reference()
    rng=random.Random(0xc16)
    pairs=[(a,b) for a in EDGES for b in EDGES]
    pairs += [(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(1000)]
    with (OUT/'crc.vec').open('w') as f:
        for op in range(16):
            for a,b in pairs:
                f.write(f'{a:08x} {b:08x} {op:x} {crc_model(a,b,op):08x}\n')
    p=Program(experimental_crc=True)
    for name in ('CRCB','CRCH','CRCW'):
        for a,b in pairs[:144]+pairs[-32:]:
            p.constant(1,a); p.constant(2,b); p.emit(name)
            p.emit(name,1,1,2)  # acumulador e destino coincidem
            p.emit(name,2,1,2)  # dado e destino coincidem
            p.emit(name,0,1,2)  # x0 não pode ser escrito
        p.emit(name,3,0,0)
    # Mesma mensagem em bytes e em duas palavras little-endian + byte.
    for grouped in (False,True):
        p.constant(1,0xffff)
        chunks=[b'1234',b'5678',b'9'] if grouped else [bytes([c]) for c in b'123456789']
        for chunk in chunks:
            p.constant(2,int.from_bytes(chunk,'little'))
            p.emit('CRCW' if len(chunk)==4 else 'CRCB',1,1,2)
        p.constant(4,0x10010000)
        p.emit('SW',0,4,1,imm=4 if grouped else 0)
        p.emit('LW',5,4,imm=4 if grouped else 0)
    p.save('crc',65536)
    assert p.memory[0x10010000]==0xb1 and p.memory[0x10010001]==0x29
    assert p.regs[5]==0x29b1
    print(f'PASS experimental CRC: {16*len(pairs)} vectors, {sum(p.counts[n] for n in ("CRCB","CRCH","CRCW"))} CRC retirements expected')


if __name__=='__main__': main()
