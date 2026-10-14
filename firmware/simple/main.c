/* Programa próprio para o contrato experimental CRC; não é firmware oficial. */
typedef unsigned int u32;
_Static_assert(sizeof(u32)==4, "RV32 required");
static volatile u32 initialized=0x12345678u;
static volatile u32 scratch[8];
static const unsigned char message[]="123456789";

static u32 crcb(u32 seed,u32 data)
{
    u32 value;
    __asm__ volatile(".insn r 0x33, 0, 0x40, %0, %1, %2" : "=r"(value) : "r"(seed),"r"(data));
    return value;
}
static u32 crch(u32 seed,u32 data)
{
    u32 value;
    __asm__ volatile(".insn r 0x33, 1, 0x40, %0, %1, %2" : "=r"(value) : "r"(seed),"r"(data));
    return value;
}
static u32 crcw(u32 seed,u32 data)
{
    u32 value;
    __asm__ volatile(".insn r 0x33, 2, 0x40, %0, %1, %2" : "=r"(value) : "r"(seed),"r"(data));
    return value;
}
__attribute__((noinline)) static u32 product(u32 a,u32 b)
{
    volatile u32 local[2]={a,b}; /* Exercita pilha e load/store além do MUL. */
    return local[0]*local[1];
}
int main(void)
{
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
    u32 c=0xffff;
    for(u32 i=0;i<9;++i) c=crcb(c,message[i]);
    if(c!=0x29b1) return (int)0xdead0005u;
    c=crch(0xffff,0x3231); c=crch(c,0x3433);
    c=crch(c,0x3635); c=crch(c,0x3837); c=crcb(c,0x39);
    if(c!=0x29b1) return (int)0xdead0006u;
    c=crcw(0xffff,0x34333231); c=crcw(c,0x38373635); c=crcb(c,0x39);
    if(c!=0x29b1) return (int)0xdead0007u;
    return 0x600dc0de;
}
