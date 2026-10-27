# Firmware próprio

`make firmware` compila com RV32I_Zmmul/ILP32. `make regression` compila e executa
automaticamente. Testa inicialização .data/.bss, loads da ROM, pilha/chamadas,
aritmética, loops, stores parciais e os quatro tipos de multiplicação.

Sucesso: grava `0x600dc0de` em `0x10011ff0`; falha: `0xdead0001` a `0xdead0006`.
Depois permanece em loop; não depende de ECALL/EBREAK. Testbench tem timeout.
Checksum esperado é calculado independentemente em Python na compilação.

```sh
make firmware
make run
make wave
```

Evidências: results/logs/firmware_build.log, smoke.disasm, tb_firmware.log.
Waveform reproduzível: results/waveforms/smoke.vcd.
Este é o smoke próprio. O [firmware oficial](../official/README.md) também foi
integrado e passou, com outro protocolo de término: x4 final e loop, sem usar
a assinatura na DMEM deste programa.
