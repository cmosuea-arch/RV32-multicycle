.option norvc
.option norelax
.section .text.start,"ax",@progbits
.globl _start
_start:
    # Inicializa pilha, copia .data da ROM e limpa .bss; RAM não tem reset físico.
    la sp, _stack_top
    la t0, _data_load
    la t1, _data_start
    la t2, _data_end
1:
    bgeu t1, t2, 2f
    lw t3, 0(t0)
    sw t3, 0(t1)
    addi t0, t0, 4
    addi t1, t1, 4
    j 1b
2:
    la t1, _bss_start
    la t2, _bss_end
3:
    bgeu t1, t2, 4f
    sw zero, 0(t1)
    addi t1, t1, 4
    j 3b
4:
    call main
    # Endereço do protocolo vem do linker, separado da região de pilha.
    la t0, _signature
    sw a0, 0(t0)
5:
    j 5b
