# CMOS RISC-V — ChampionCHIP

Implementação incremental multiciclo conforme `Champion-chip-guia-fase-2.pdf`.
Estado e cobertura: [docs/status.md](docs/status.md).

## Executar

Requisitos: Python 3, Icarus Verilog (`iverilog`, `vvp`), Verilator e Make.
Firmware próprio usa `riscv64-unknown-elf-gcc` com alvo RV32.

```sh
make test          # testes unitários e de integração existentes
make lint         # lint dos módulos sintetizáveis
make regression   # todos os testes, firmware e lint
```

Logs ficam em `results/logs/`; artefatos temporários em `build/`.
Nenhuma instrução CRC ou de sistema é contabilizada sem definição confirmada.
O projeto não incorpora RTL do Ibex.
