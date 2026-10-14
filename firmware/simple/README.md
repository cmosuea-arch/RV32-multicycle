# Firmware do simple_system

Programa próprio RV32I_Zmmul com CRCB/CRCH/CRCW sob o
[contrato provisório CMOS](../../docs/architecture/crc_provisional.md).

`start.S` configura pilha, copia `.data`, limpa `.bss`, chama `main` e escreve
seu retorno em `_signature`, definido no linker. Depois permanece em loop.
`main.c` verifica inicialização, pilha, MUL, escritas parciais e CRC por três
agrupamentos de `123456789`. Esperado: 0x29b1, seed 0xffff.

Sucesso: 0x600dc0de. Falhas: 0xdead0001–0xdead0007 identificam os testes na ordem
do código. `.insn r` emite CRC sem exigir um assembler customizado.

`link.ld`: ROM 2 KiB em 0x00400000, RAM 1 KiB em 0x10010000,
pilha 0x100103e0, assinatura 0x100103f0. Reserva mínima de pilha: 256 bytes.

```bash
make simple-firmware
make simple-system
```

Arquivos em `build/simple.{elf,bin,hex,map}`; build/disassembly em `results/logs/`.
O gerador rejeita excesso de ROM e preenche 512 palavras little-endian. Na
validação inicial: 608 bytes de imagem ROM (604 text + 4 data), 32 bytes BSS.
ROM entra como constantes na síntese; trocar programa exige ressíntese.
Não substitui `firmware/smoke/` nem o firmware oficial.
