/* Own smoke firmware: startup, ROM constants, .data/.bss, stack and Zmmul. */
typedef unsigned int u32;
typedef int s32;
typedef unsigned char u8;
_Static_assert(sizeof(u32) == 4, "RV32 required");

static volatile u32 initialized = 0x12345678u;
static volatile u32 scratch[16];
static const u8 bytes[8] = {0x80, 0x7f, 0xff, 1, 0x12, 0x34, 0x56, 0x78};

__attribute__((noinline)) static u32 kernel(u32 x, u32 y)
{
    volatile u32 local[4];
    local[0] = x;
    local[1] = y;
    local[2] = x * y;
    local[3] = (x << 5) ^ (y >> 3);
    return local[2] + local[3];
}

int main(void)
{
    u32 sum = 0;
    if (initialized != 0x12345678u) return (int)0xdead0001u;
    for (u32 i = 0; i < 16; ++i) {
        if (scratch[i] != 0) return (int)0xdead0002u;
        scratch[i] = kernel(i + 1, 0x10203u + i);
        sum ^= scratch[i];
    }
    /* Independently calculated by scripts/sim/build_firmware.py. */
    if (sum != EXPECTED_SUM) return (int)0xdead0003u;
    volatile const u8 *rom = bytes;
    if ((s32)(signed char)rom[0] != -128 || rom[2] != 255)
        return (int)0xdead0004u;
    volatile unsigned short *half = (volatile unsigned short *)&scratch[0];
    volatile u8 *byte = (volatile u8 *)&scratch[0];
    scratch[0] = 0xaabbccddu;
    half[1] = 0x1234;
    byte[1] = 0x80;
    if (scratch[0] != 0x123480ddu) return (int)0xdead0005u;

    u32 hi, mixed, uns;
    u32 a = 0xffffffffu, b = 0xffffffffu;
    __asm__ volatile ("mulh %0,%1,%2" : "=r"(hi) : "r"(a), "r"(b));
    __asm__ volatile ("mulhsu %0,%1,%2" : "=r"(mixed) : "r"(a), "r"(b));
    __asm__ volatile ("mulhu %0,%1,%2" : "=r"(uns) : "r"(a), "r"(b));
    if (hi != 0 || mixed != 0xffffffffu || uns != 0xfffffffeu)
        return (int)0xdead0006u;
    return 0x600dc0de;
}
