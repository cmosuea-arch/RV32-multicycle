# CMOS RISC-V — ChampionCHIP

Implementação incremental multiciclo conforme `Champion-chip-guia-fase-2.pdf`.
**41/47 instruções (87,23%)**, com RTL integrado, testes autoverificáveis e
firmware próprio validado. Estado: [docs/status.md](docs/status.md).
Matriz por instrução: [docs/isa/coverage.md](docs/isa/coverage.md). A versão para
Excel está em [docs/isa/coverage.xlsx](docs/isa/coverage.xlsx).

## Executar

Requisitos: Python 3, Icarus Verilog (`iverilog`, `vvp`), Verilator e Make.
Firmware próprio usa `riscv64-unknown-elf-gcc` com alvo RV32.

```sh
make test          # testes unitários e de integração existentes
make lint         # lint dos módulos sintetizáveis
make regression   # todos os testes, firmware e lint
make smoke        # quatro bancadas rápidas, sem compilador RISC-V
make wave         # executa firmware próprio e gera waveform VCD
```

Logs ficam em `results/logs/`; artefatos temporários em `build/`.
Nenhuma instrução CRC ou de sistema é contabilizada sem definição confirmada.
O projeto não incorpora RTL do Ibex. A assinatura do firmware próprio é
`0x600dc0de` em `0x10011ff0`; não substitui a validação oficial da competição.

## Organização

- `rtl/`: blocos, decoder, FSM, core e top de integração.
- `tb/unit/` e `tb/integration/`: 28 testbenches autoverificáveis.
- `scripts/sim/`: modelos Python, vetores e compilação do firmware.
- `firmware/smoke/`: programa C/assembly e linker script RV32I_Zmmul.
- `docs/architecture/`: contratos, datapath, mapa e decisões justificadas.
- `docs/modules/`: especificação, diagrama, testes e commit de cada bloco.
- `results/logs/regression.json`: resultado e hashes dos arquivos testados.

O top usa por padrão IMEM de 4 MiB e DMEM de 8 KiB; testbenches parametrizam
uma ROM menor. Interfaces externas ainda não representam a pinagem física final.

## Limite desta versão

CRC, sistema/sincronização, firmware oficial e pinagem final têm pendências
documentadas em [docs/architecture/official_questions.md](docs/architecture/official_questions.md).
OpenLane/GDSII não foram iniciados, conforme os pré-requisitos do `AGENTS.md`.
Diagramas Mermaid estão versionados; os desenhos ChipInventor da submissão
ainda precisam ser produzidos. Esta versão não recebe a tag de RTL final da competição.
