"""Codificações confirmadas: RV32I, Zmmul e Xicrc oficial."""
# Tabela compartilhada pelos geradores e pela cobertura: nome -> campos da instrução.
# Em R/I, o último número é o seletor interno da ALU, não um campo da ISA.
R = {'ADD':(0,0,1),'SUB':(0,32,2),'SLL':(1,0,6),'SLT':(2,0,9),
     'SLTU':(3,0,10),'XOR':(4,0,5),'SRL':(5,0,7),'SRA':(5,32,8),
     'OR':(6,0,4),'AND':(7,0,3)}
I = {'ADDI':(0,1),'SLTI':(2,9),'SLTIU':(3,10),'XORI':(4,5),
     'ORI':(6,4),'ANDI':(7,3),'SLLI':(1,6),'SRLI':(5,7),'SRAI':(5,8)}
BRANCH = {'BEQ':0,'BNE':1,'BLT':4,'BGE':5,'BLTU':6,'BGEU':7}
LOAD = {'LB':0,'LH':1,'LW':2,'LBU':4,'LHU':5}
STORE = {'SB':0,'SH':1,'SW':2}
MULT = {'MUL':0,'MULH':1,'MULHSU':2,'MULHU':3}
SYSTEM = {'ECALL':0x00000073,'EBREAK':0x00100073}
CATEGORIES = {'Register':list(R),'Immediate':list(I),'Upper':['LUI','AUIPC'],
              'Branch':list(BRANCH),'Jump':['JAL','JALR'],'Load':list(LOAD),
              'Store':list(STORE),'Multiplication':list(MULT),
              'CRC':['CRCB','CRCH','CRCW'],
              'Sistema/Sincronização':['FENCE','ECALL','EBREAK']}


def fields(name):
    # Centraliza opcode/funct3/funct7; None indica campo ausente ou não definido.
    if name in R: return 0x33,R[name][0],R[name][1]
    if name in I:
        return 0x13,I[name][0], (32 if name=='SRAI' else 0) if name.endswith('LI') or name=='SRAI' else None
    if name in MULT: return 0x33,MULT[name],1
    if name in BRANCH: return 0x63,BRANCH[name],None
    if name in LOAD: return 3,LOAD[name],None
    if name in STORE: return 0x23,STORE[name],None
    if name.startswith('CRC'): return 0x33,{'CRCB':0,'CRCH':1,'CRCW':2}[name],64
    if name in SYSTEM: return 0x73,0,None  # imm12/rs1/rd também são fixos, ver SYSTEM.
    if name=='FENCE': return 0x0f,0,None
    return {'LUI':(0x37,None,None),'AUIPC':(0x17,None,None),
            'JAL':(0x6f,None,None),'JALR':(0x67,0,None)}.get(name,(None,None,None))


def encode(name, rd=3, rs1=1, rs2=2, imm=0):
    # Monta uma palavra de instrução; sua execução é modelada em programs.py.
    from vectors import encode_imm
    if name in SYSTEM: return SYSTEM[name]
    if name=='FENCE': return ((imm&0xfff)<<20)|(rs1<<15)|(rd<<7)|0x0f
    opcode,f3,f7=fields(name)
    if name in R or name in MULT or name in CATEGORIES['CRC']:
        return (f7<<25)|(rs2<<20)|(rs1<<15)|(f3<<12)|(rd<<7)|opcode
    # Formatos I/LOAD/JALR usam imediato de 12 bits; shifts reservam bits para funct7.
    if name in I or name in LOAD or name=='JALR':
        if name in ('SLLI','SRLI','SRAI'): imm=(imm&31)|(f7<<5)
        return (encode_imm('I',imm,rd,rs1,rs2,f3)&~127)|opcode
    if name in ('LUI','AUIPC'): return (encode_imm('U',imm,rd)&~127)|opcode
    if name in BRANCH: return encode_imm('B',imm,0,rs1,rs2,f3)
    if name=='JAL': return encode_imm('J',imm,rd)
    if name in STORE: return encode_imm('S',imm,0,rs1,rs2,f3)
    raise ValueError(name)


def identify(word):
    """Nome pela palavra completa; SYSTEM exige validar também imm12, rs1 e rd."""
    if word & 127 == 0x73:
        for name, encoding in SYSTEM.items():
            if word == encoding:
                return name
        raise ValueError(f'SYSTEM não suportada: {word:08x}')
    opcode, f3, f7 = word & 127, (word >> 12) & 7, word >> 25
    for names in CATEGORIES.values():
        for name in names:
            op, a, b = fields(name)
            if op == opcode and a in (None, f3) and b in (None, f7):
                return name
    raise ValueError(f'Instrução não reconhecida: {word:08x}')
