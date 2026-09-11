#!/usr/bin/env python3
"""Create per-instruction programs and architectural retirement expectations."""
from pathlib import Path
import json
import random
from isa import R,I,CATEGORIES,fields,encode
from vectors import signed,MASK,EDGES,alu_model

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build'
BASE=0x00400000


class Program:
    def __init__(self):
        self.words=[]
        self.trace=[]
        self.regs=[0]*32
        self.counts={}

    def emit(self,name,rd=3,rs1=1,rs2=2,imm=0):
        pc=BASE+4*len(self.words)
        inst=encode(name,rd,rs1,rs2,imm)
        a,b=self.regs[rs1],self.regs[rs2]
        if name in R: value=alu_model(a,b,R[name][2])
        elif name in I:
            operand=imm&31 if name in ('SLLI','SRLI','SRAI') else signed(imm,12)&MASK
            value=alu_model(a,operand,I[name][1])
        elif name=='LUI': value=imm&0xfffff000
        elif name=='AUIPC': value=(pc+(imm&0xfffff000))&MASK
        else: raise ValueError(name)
        if rd: self.regs[rd]=value
        self.words.append(inst)
        self.trace.append((pc,inst,rd,self.regs[rd]))
        self.counts[name]=self.counts.get(name,0)+1

    def constant(self,rd,value):
        value &= MASK
        self.emit('ADDI',rd,0,imm=(value>>24))
        for shift in (16,8,0):
            for _ in range(8): self.emit('ADD',rd,rd,rd)
            self.emit('ADDI',rd,rd,imm=(value>>shift)&255)

    def save(self):
        if len(self.words)>65536: raise ValueError('program exceeds test ROM')
        (OUT/'isa.hex').write_text(''.join(f'{w:08x}\n' for w in self.words+[0]*(65536-len(self.words))))
        (OUT/'isa.trace').write_text(''.join(f'{pc:08x} {ins:08x} {rd:02x} {value:08x}\n' for pc,ins,rd,value in self.trace))
        (OUT/'isa_counts.json').write_text(json.dumps(self.counts,indent=2)+'\n')


def main():
    OUT.mkdir(exist_ok=True)
    enabled=json.loads((ROOT/'docs/isa/enabled.json').read_text())
    rng=random.Random(4711)
    p=Program()
    for name in enabled:
        if name in R:
            pairs=[(a,b) for a in EDGES[:10] for b in [0,1,31,32,0xffffffff,0x80000000]]
            pairs += [(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(12)]
            for a,b in pairs:
                p.constant(1,a); p.constant(2,b); p.emit(name)
            p.emit(name,0); p.emit(name,1,1,2) # x0 and destination/source overlap
        elif name in I:
            for a in EDGES:
                for v in ([0,1,31] if name in ('SLLI','SRLI','SRAI') else [0,1,-1,-2048,2047]):
                    p.constant(1,a); p.emit(name,imm=v)
            p.emit(name,0,imm=1); p.emit(name,1,1,imm=1)
        elif name in ('LUI','AUIPC'):
            for v in [0,0x1000,0x7ffff000,0x80000000,0xfffff000]:
                p.emit(name,imm=v)
            p.emit(name,0,imm=0xfffff000)
    p.save()
    with (OUT/'decoder.vec').open('w') as f:
        for opcode in range(128):
            for f3 in range(8):
                for f7 in range(128):
                    inst=(f7<<25)|(2<<20)|(1<<15)|(f3<<12)|(3<<7)|opcode
                    matches=[name for name in enabled if fields(name)[0]==opcode
                             and fields(name)[1] in (None,f3) and fields(name)[2] in (None,f7)]
                    ctrl=1
                    if matches:
                        name=matches[0]
                        op=R[name][2] if name in R else I[name][1] if name in I else 1 if name=='AUIPC' else 0
                        ctrl=(op<<10)|(int(name=='AUIPC')<<9)|(int(name in I or name in ('LUI','AUIPC'))<<8)|(1<<7)
                    f.write(f'{inst:08x} {ctrl:04x}\n')
    print(f'PASS generated {len(p.words)} instructions; targets={len(enabled)}')


if __name__=='__main__': main()
