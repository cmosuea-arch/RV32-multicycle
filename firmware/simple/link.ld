OUTPUT_ARCH(riscv)
ENTRY(_start)
MEMORY {
    /* Capacidades reduzidas do simple_system; as bases oficiais são preservadas. */
    ROM (rx) : ORIGIN = 0x00400000, LENGTH = 2K
    RAM (rw) : ORIGIN = 0x10010000, LENGTH = 1K
}
PHDRS { text PT_LOAD FLAGS(5); data PT_LOAD FLAGS(6); }
SECTIONS {
    .text : { KEEP(*(.text.start)) *(.text .text.*) } > ROM :text
    .rodata : { *(.rodata .rodata.*) . = ALIGN(4); } > ROM :text
    /* Dados executam na RAM, mas seus valores iniciais são carregados da ROM. */
    .data : {
        . = ALIGN(4); _data_start = .;
        *(.data .data.* .sdata .sdata.*)
        . = ALIGN(4); _data_end = .;
    } > RAM AT> ROM :data
    _data_load = LOADADDR(.data);
    /* O startup limpa a região NOLOAD, inclusive após um reset com RAM suja. */
    .bss (NOLOAD) : {
        . = ALIGN(4); _bss_start = .;
        *(.bss .bss.* .sbss .sbss.* COMMON)
        . = ALIGN(4); _bss_end = .;
    } > RAM :data
    /* A assinatura fica acima da pilha e só recebe o status final de main. */
    _signature = ORIGIN(RAM) + LENGTH(RAM) - 16;
    _stack_top = ORIGIN(RAM) + LENGTH(RAM) - 32;
    ASSERT(_bss_end + 256 <= _stack_top, "reserve at least 256 bytes for stack")
}
