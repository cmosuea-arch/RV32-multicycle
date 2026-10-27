OUTPUT_ARCH(riscv)
ENTRY(_start)
MEMORY {
    /* Capacidades desta bancada: ROM 16 KiB e RAM 8 KiB, nas bases da arquitetura. */
    ROM (rx)  : ORIGIN = 0x00400000, LENGTH = 16K
    RAM (rw)  : ORIGIN = 0x10010000, LENGTH = 8K
}
PHDRS { text PT_LOAD FLAGS(5); data PT_LOAD FLAGS(6); }
SECTIONS {
    .text : { KEEP(*(.text.start)) *(.text .text.*) } > ROM :text
    .rodata : { *(.rodata .rodata.*) . = ALIGN(4); } > ROM :text
    /* VMA na RAM, LMA na ROM: start.S copia _data_load para _data_start. */
    .data : {
        . = ALIGN(4); _data_start = .;
        *(.data .data.* .sdata .sdata.*)
        . = ALIGN(4); _data_end = .;
    } > RAM AT> ROM :data
    _data_load = LOADADDR(.data);
    /* Reserva espaço sem gravar zeros no arquivo binário; o startup fará a limpeza. */
    .bss (NOLOAD) : {
        . = ALIGN(4); _bss_start = .;
        *(.bss .bss.* .sbss .sbss.* COMMON)
        . = ALIGN(4); _bss_end = .;
    } > RAM :data
    _stack_top = ORIGIN(RAM) + LENGTH(RAM) - 32;
    ASSERT(_bss_end + 1024 < _stack_top, "reserve at least 1 KiB for stack")
}
