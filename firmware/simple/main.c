/* Programa próprio usando o contrato CRC oficial; não substitui o firmware oficial. */
typedef unsigned int u32;
_Static_assert(sizeof(u32)==4, "RV32 required");
static volatile u32 initialized=0x12345678u;
static volatile u32 scratch[8];
static const unsigned char message[]="123456789";

/* API C: (seed, data); a instrução usa rs1=data e rs2=seed nos operandos abaixo. */
static u32 crcb(u32 seed,u32 data)
{
    u32 value;
    __asm__ volatile(".insn r 0x33, 0, 0x40, %0, %1, %2" : "=r"(value) : "r"(data),"r"(seed));
    return value;
}
static u32 crch(u32 seed,u32 data)
{
    /* Mesmo acumulador de 16 bits, consumindo os 16 bits baixos de data. */
    u32 value;
    __asm__ volatile(".insn r 0x33, 1, 0x40, %0, %1, %2" : "=r"(value) : "r"(data),"r"(seed));
    return value;
}
static u32 crcw(u32 seed,u32 data)
{
    /* Consome os quatro bytes de data do mais significativo para o menos. */
    u32 value;
    __asm__ volatile(".insn r 0x33, 2, 0x40, %0, %1, %2" : "=r"(value) : "r"(data),"r"(seed));
    return value;
}
__attribute__((noinline)) static u32 product(u32 a,u32 b)
{
    volatile u32 local[2]={a,b}; /* Exercita pilha e load/store além do MUL. */
    return local[0]*local[1];
}
int main(void)
{
    /* Confere o trabalho do startup antes de exercitar pilha, MUL e escritas parciais. */
    if(initialized!=0x12345678u) return (int)0xdead0001u;
    for(u32 i=0;i<8;++i) {
        if(scratch[i]!=0) return (int)0xdead0002u;
        scratch[i]=product(i+1,3);
        if(scratch[i]!=(i+1)+(i+1)+(i+1)) return (int)0xdead0003u;
    }
    volatile unsigned char *byte=(volatile unsigned char *)&scratch[0];
    volatile unsigned short *half=(volatile unsigned short *)&scratch[0];
    scratch[0]=0xaabbccddu; byte[1]=0x80; half[1]=0x1234;
    if(scratch[0]!=0x123480ddu) return (int)0xdead0004u;
    /* A seed inicia a mensagem uma vez; cada instrução devolve a seed da próxima. */
    u32 c=0xffff;
    for(u32 i=0;i<9;++i) c=crcb(c,message[i]);
    if(c!=0x29b1) return (int)0xdead0005u;
    /* A mesma mensagem em pares e words deve manter o CRC final 29B1. */
    c=crch(0xffff,0x3132); c=crch(c,0x3334);
    c=crch(c,0x3536); c=crch(c,0x3738); c=crcb(c,0x39);
    if(c!=0x29b1) return (int)0xdead0006u;
    c=crcw(0xffff,0x31323334); c=crcw(c,0x35363738); c=crcb(c,0x39);
    if(c!=0x29b1) return (int)0xdead0007u;
    /* start.S escreve este retorno na assinatura, observada pelo TB e pelo top. */
    return 0x600dc0de;
}
