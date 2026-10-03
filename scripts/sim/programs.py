#!/usr/bin/env python3
"""Create per-instruction programs and architectural retirement expectations."""
from pathlib import Path
import json
import random
from isa import R,I,BRANCH,LOAD,STORE,MULT,CATEGORIES,fields,encode
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
        self.ops=[]
        self.memory={}

    def emit(self,name,rd=3,rs1=1,rs2=2,imm=0):
        # Guarda a palavra binária e a operação simbólica usada pelo modelo.
        pc=BASE+4*len(self.words)
        inst=encode(name,rd,rs1,rs2,imm)
        self.words.append(inst)
        self.ops.append((name,rd,rs1,rs2,imm))

    def evaluate(self):
        # Segue o PC e atualiza RF/memória para prever cada aposentadoria do RTL.
        pc=BASE
        while pc != BASE+4*len(self.words):
            if pc<BASE or pc>=BASE+4*len(self.words) or pc%4: raise ValueError(f'bad model PC {pc:x}')
            if len(self.trace)>250000: raise ValueError('model loop')
            index=(pc-BASE)//4
            name,rd,rs1,rs2,imm=self.ops[index]
            a,b=self.regs[rs1],self.regs[rs2]
            next_pc=pc+4
            if name in R: value=alu_model(a,b,R[name][2])
            elif name in I:
                operand=imm&31 if name in ('SLLI','SRLI','SRAI') else signed(imm,12)&MASK
                value=alu_model(a,operand,I[name][1])
            elif name=='LUI': value=imm&0xfffff000
            elif name=='AUIPC': value=(pc+(imm&0xfffff000))&MASK
            elif name in BRANCH:
                taken={'BEQ':a==b,'BNE':a!=b,'BLT':signed(a)<signed(b),
                       'BGE':signed(a)>=signed(b),'BLTU':a<b,'BGEU':a>=b}[name]
                if taken: next_pc=pc+imm
                rd=0; value=0
            elif name=='JAL': value=pc+4; next_pc=pc+imm
            elif name=='JALR': value=pc+4; next_pc=((a+signed(imm,12))&MASK)&~1
            elif name in LOAD:
                addr=(a+signed(imm,12))&MASK
                size={'LB':1,'LBU':1,'LH':2,'LHU':2,'LW':4}[name]
                if addr%size: raise ValueError('model load alignment')
                if BASE<=addr<BASE+len(self.words)*4:
                    raw=b''.join(w.to_bytes(4,'little') for w in self.words[(addr-BASE)//4:(addr-BASE)//4+2])
                    raw=raw[addr%4:addr%4+size]
                else: raw=bytes(self.memory[addr+i] for i in range(size))
                value=int.from_bytes(raw,'little',signed=name in ('LB','LH'))&MASK
            elif name in STORE:
                addr=(a+signed(imm,12))&MASK
                size={'SB':1,'SH':2,'SW':4}[name]
                if addr%size: raise ValueError('model store alignment')
                for i in range(size): self.memory[addr+i]=(b>>(8*i))&255
                rd=0; value=0
            elif name in MULT:
                aa=signed(a) if name in ('MUL','MULH','MULHSU') else a
                bb=signed(b) if name in ('MUL','MULH') else b
                value=((aa*bb)>>(0 if name=='MUL' else 32))&MASK
            else: raise ValueError(name)
            if rd: self.regs[rd]=value
            self.trace.append((pc,self.words[index],rd,self.regs[rd]))
            self.counts[name]=self.counts.get(name,0)+1
            pc=next_pc&MASK

    def constant(self,rd,value):
        value &= MASK
        self.emit('ADDI',rd,0,imm=(value>>24))
        for shift in (16,8,0):
            for _ in range(8): self.emit('ADD',rd,rd,rd)
            self.emit('ADDI',rd,rd,imm=(value>>shift)&255)

    def save(self):
        # ROM, trace e memória final são entradas de tb_isa; counts alimenta o relatório.
        self.evaluate()
        if len(self.words)>131072: raise ValueError('program exceeds test ROM')
        (OUT/'isa.hex').write_text(''.join(f'{w:08x}\n' for w in self.words+[0]*(131072-len(self.words))))
        (OUT/'isa.trace').write_text(''.join(f'{pc:08x} {ins:08x} {rd:02x} {value:08x}\n' for pc,ins,rd,value in self.trace))
        (OUT/'isa_counts.json').write_text(json.dumps(self.counts,indent=2)+'\n')
        (OUT/'isa_memory.vec').write_text(''.join(f'{a:08x} {v:02x}\n' for a,v in sorted(self.memory.items())))


def main():
    OUT.mkdir(exist_ok=True)
    enabled=json.loads((ROOT/'docs/isa/enabled.json').read_text())
    rng=random.Random(4711)
    p=Program()
    for name in enabled:
        if name in R or name in MULT:
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
        elif name in BRANCH:
            for a,b in [(0,0),(1,2),(2,1),(0xffffffff,1),(0x80000000,0x7fffffff)]:
                p.constant(1,a); p.constant(2,b)
                p.emit(name,0,1,2,imm=8)
                p.emit('ADDI',3,0,imm=17)
                p.emit('ADDI',4,0,imm=34)
            if name=='BEQ':
                p.constant(1,1); p.constant(2,0); p.emit('ADDI',2,2,imm=1)
            elif name=='BNE':
                p.constant(1,2); p.constant(2,0); p.emit('ADDI',2,2,imm=1)
            elif name in ('BLT','BLTU'):
                p.constant(1,0); p.constant(2,2); p.emit('ADDI',1,1,imm=1)
            else:
                p.constant(1,2); p.constant(2,1); p.emit('ADDI',1,1,imm=-1)
            p.emit(name,0,1,2,imm=-4)
        elif name=='JAL':
            p.emit('JAL',5,imm=12)
            p.emit('ADDI',3,0,imm=123)
            p.emit('JAL',0,imm=8)
            p.emit('JAL',6,imm=-8)
        elif name=='JALR':
            # rs1=rd overlap; odd target bit is cleared; positive/negative immediates.
            for offset in [12,-12]:
                target=BASE+4*(len(p.words)+28+2)
                p.constant(1,target-offset+1)
                p.emit('JALR',1,1,imm=offset)
                p.emit('ADDI',3,0,imm=999) # must be skipped
                p.emit('ADDI',4,1,imm=0) # consume link
            # Backward jump via a small call/return-shaped sequence.
            origin=BASE+4*(len(p.words)+56)
            p.constant(1,origin+12)
            p.constant(2,origin+4)
            p.emit('JALR',5,1,imm=0)
            p.emit('ADDI',3,0,imm=77)
            p.emit('JAL',0,imm=8)
            p.emit('JALR',6,2,imm=0)
        elif name in LOAD:
            size={'LB':1,'LBU':1,'LH':2,'LHU':2,'LW':4}[name]
            for word in [0,0x7f0180ff,0xf4f3f2f1,0x80007fff,0xffffffff]:
                p.constant(1,0x10010000); p.constant(2,word); p.emit('SW',0,1,2)
                for offset in range(0,4,size): p.emit(name,3,1,imm=offset)
                p.emit(name,0,1) # load to x0 still performs access
                p.constant(1,0x10010004); p.emit(name,3,1,imm=-4)
            p.constant(1,BASE)
            p.emit(name,3,1) # constant load from ROM
        elif name in STORE:
            size={'SB':1,'SH':2,'SW':4}[name]
            for offset in range(0,4,size):
                p.constant(1,0x10010000); p.constant(2,0xa5a5a5a5); p.emit('SW',0,1,2)
                p.constant(2,0x87654321); p.emit(name,0,1,2,imm=offset); p.emit('LW',3,1)
            p.constant(1,0x10011ffc); p.emit(name,0,1,2); p.emit(name,0,1,2,imm=-4)
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
                        if name in BRANCH or name in ('JAL','JALR') or name in LOAD or name in STORE: op=1
                        ctrl=(op<<10)|(int(name in ('AUIPC','JAL') or name in BRANCH)<<9)|(int(name not in R and name not in MULT)<<8)|(int(name not in BRANCH and name not in STORE)<<7)|(int(name in BRANCH)<<6)|(int(name=='JAL')<<5)|(int(name=='JALR')<<4)|(int(name in LOAD)<<3)|(int(name in STORE)<<2)|(int(name in MULT)<<1)
                    f.write(f'{inst:08x} {ctrl:04x}\n')
    print(f'PASS generated {len(p.words)} instructions; targets={len(enabled)}')


if __name__=='__main__': main()
