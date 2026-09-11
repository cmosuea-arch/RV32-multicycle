#!/usr/bin/env python3
"""Independent integer models; deterministic vectors consumed by SV benches."""
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build'
MASK = (1 << 32) - 1
EDGES = [0, 1, 2, 31, 32, 33, 0x7fffffff, 0x80000000,
         0xffffffff, 0xfffffffe, 0x55555555, 0xaaaaaaaa]


def signed(n, bits=32):
    n &= (1 << bits) - 1
    return n - (1 << bits) if n & (1 << (bits - 1)) else n


def alu_model(a, b, op):
    return [lambda: b, lambda: a + b, lambda: a - b,
            lambda: a & b, lambda: a | b, lambda: a ^ b,
            lambda: a * (2 ** (b % 32)), lambda: a // (2 ** (b % 32)),
            lambda: signed(a) // (2 ** (b % 32)),
            lambda: int(signed(a) < signed(b)), lambda: int(a < b)][op]() & MASK


def main():
    OUT.mkdir(exist_ok=True)
    rng = random.Random(0xC005)
    pairs = [(a, b) for a in EDGES for b in EDGES]
    pairs += [(rng.getrandbits(32), rng.getrandbits(32)) for _ in range(1000)]
    with (OUT / 'alu.vec').open('w') as f:
        for op in range(16):
            for a, b in pairs:
                expected = alu_model(a, b, op) if op < 11 else 0
                f.write(f'{a:08x} {b:08x} {op:x} {expected:08x}\n')
    with (OUT / 'imm.vec').open('w') as f:
        for fmt, bits, step in [('I',12,1),('S',12,1),('B',13,2),('U',32,4096),('J',21,2)]:
            vals = [0, step, -step, -(1 << (bits-1)), (1 << (bits-1))-step]
            vals += [signed(rng.getrandbits(bits), bits)//step*step for _ in range(1000)]
            # Walk each independent payload bit as well as sign and limits.
            vals += [signed(1 << bit, bits) for bit in range(bits) if (1 << bit) >= step]
            for value in vals:
                inst = encode_imm(fmt, value)
                f.write(f'{inst:08x} {value & MASK:08x}\n')
        f.write('ffffffff 00000000\n')
    with (OUT/'branch.vec').open('w') as f:
        for code in range(8):
            for a,b in pairs:
                expected={0:a==b,1:a!=b,4:signed(a)<signed(b),5:signed(a)>=signed(b),6:a<b,7:a>=b}.get(code,False)
                f.write(f'{a:08x} {b:08x} {code:x} {int(expected):x}\n')
    print('PASS deterministic vectors generated')


def encode_imm(fmt, value, rd=3, rs1=1, rs2=2, funct3=0):
    v = value & MASK
    if fmt == 'I': return ((v & 4095)<<20)|(rs1<<15)|(funct3<<12)|(rd<<7)|0x13
    if fmt == 'S': return ((v>>5 & 127)<<25)|(rs2<<20)|(rs1<<15)|(funct3<<12)|((v&31)<<7)|0x23
    if fmt == 'B': return ((v>>12 & 1)<<31)|((v>>5 & 63)<<25)|(rs2<<20)|(rs1<<15)|(funct3<<12)|((v>>1 & 15)<<8)|((v>>11 & 1)<<7)|0x63
    if fmt == 'U': return (v & 0xfffff000)|(rd<<7)|0x37
    if fmt == 'J': return ((v>>20 & 1)<<31)|((v>>1 & 1023)<<21)|((v>>11 & 1)<<20)|((v>>12 & 255)<<12)|(rd<<7)|0x6f
    raise ValueError(fmt)


if __name__ == '__main__':
    main()
