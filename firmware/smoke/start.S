.option norvc
.option norelax
.section .text.start,"ax",@progbits
.globl _start
_start:
    # O linker define pilha, endereço de carga na ROM e destino de .data na RAM.
    la sp, _stack_top
    la t0, _data_load
    la t1, _data_start
    la t2, _data_end
1:
    # Copia uma word por vez; variáveis inicializadas ainda não estão na RAM do reset.
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
    # .bss não vem no binário: o startup fornece seus zeros a cada boot.
    bgeu t1, t2, 4f
    sw zero, 0(t1)
    addi t1, t1, 4
    j 3b
4:
    # main retorna o status em a0; o SW abaixo é o protocolo do smoke próprio.
    call main
    li t0, 0x10011ff0
    sw a0, 0(t0)
5:
    # O TB detecta a assinatura; o processador continua neste loop sem ECALL fictícia.
    j 5b
