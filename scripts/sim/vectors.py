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
    print('PASS deterministic vectors generated')


if __name__ == '__main__':
    main()
