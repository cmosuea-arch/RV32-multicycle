#!/usr/bin/env python3
"""Vetores e programa Xicrc com casos aleatórios e mensagens de referência."""
# crc.vec testa o bloco isolado; crc.hex/trace/memory.vec testam sua integração no core.
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
    # Repetibilidade: limites explícitos mais casos aleatórios com semente fixa.
    with (OUT/'crc.vec').open('w') as f:
        for op in range(16):
            for a,b in pairs:
                f.write(f'{a:08x} {b:08x} {op:x} {crc_model(a,b,op):08x}\n')
    # Exercita writeback, dependências e sobreposição com ambos os operandos.
    p=Program(experimental_crc=True)
    for name in ('CRCB','CRCH','CRCW'):
        for a,b in pairs[:144]+pairs[-32:]:
            p.constant(1,a); p.constant(2,b); p.emit(name)
            p.emit(name,1,1,2)  # dado e destino coincidem
            p.emit(name,2,1,2)  # acumulador e destino coincidem
            p.emit(name,0,1,2)  # x0 não pode ser escrito
        p.emit(name,3,0,0)
    # Cada mensagem usa CRCB/CRCH/CRCW: mesma ordem de bytes, acumulador em rs2.
    messages=((b'123456789',0x29b1),(bytes.fromhex('1234567890ABCDEF'),0x1e82))
    slot=0
    for message,expected in messages:
        for size in (1,2,4):
            p.constant(1,0xffff)
            for offset in range(0,len(message),size):
                chunk=message[offset:offset+size]
                p.constant(2,int.from_bytes(chunk,'big'))
                p.emit({1:'CRCB',2:'CRCH',4:'CRCW'}[len(chunk)],1,2,1)
            p.constant(4,0x10010000)
            p.emit('SW',0,4,1,imm=slot*4)
            p.emit('LW',5,4,imm=slot*4)
            slot+=1
    # Salva ROM/trace e confere o CRC conhecido também nos registradores e na RAM.
    p.save('crc',65536)
    assert p.memory[0x10010000]==0xb1 and p.memory[0x10010001]==0x29
    for slot,expected in enumerate((0x29b1,)*3+(0x1e82,)*3):
        actual=sum(p.memory[0x10010000+slot*4+i]<<(8*i) for i in range(4))
        assert actual==expected
    print(f'PASS Xicrc: {16*len(pairs)} vectors, {sum(p.counts[n] for n in ("CRCB","CRCH","CRCW"))} CRC retirements expected')


if __name__=='__main__': main()
