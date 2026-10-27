# Roteiro de testes do RTL

Para aprender os conceitos e executar primeiro os passos manuais, siga o
[laboratório guiado](../labs/rtl-to-gds/README.md). Esta página é a consulta rápida.

Este roteiro valida o perfil 47/47, o firmware oficial e o simple_system.
O contrato CRC e o firmware oficial estão verificados em RTL;
FENCE/ECALL/EBREAK passam sob o [EEI CMOS](architecture/system.md).
Interface final e resultados físicos continuam pendentes.

## 1. Preparação

Execute na raiz do repositório:

```sh
cd /home/luixf/eda/uniccass-icdesign-tools/shared_xserver/cmos-riscv
git status --short
make help
make doctor
make lint
```

O lint precisa terminar sem diagnóstico. Os comandos seguintes recompõem os
vetores determinísticos necessários; não é preciso editar arquivos em `build/`.

## 2. Testbench isolado

Para executar qualquer testbench pelo nome do módulo:

```sh
make tb TB=tb_alu
make tb TB=tb_regfile
make tb TB=tb_lsu
```

O executor compila todo o catálogo RTL, seleciona apenas o top indicado com
`iverilog -s`, executa a simulação e exige a marca `PASS`. Os logs ficam em
`results/logs/tb_<nome>.compile.log` e `results/logs/tb_<nome>.log`.

Sequência isolada recomendada:

```sh
make tb TB=tb_alu
make tb TB=tb_regfile
make tb TB=tb_imm_ext
make tb TB=tb_pc
make tb TB=tb_ir
make tb TB=tb_imem
make tb TB=tb_branch_comp
make tb TB=tb_lsu
make tb TB=tb_dmem
make tb TB=tb_address_decoder
make tb TB=tb_multiplier
make tb TB=tb_decoder
make tb TB=tb_control_unit
make tb TB=tb_crc
```

Para executar os 14 testbenches unitários em uma chamada:

```sh
make unit
```

## 3. Integração incremental

A ordem abaixo acompanha o crescimento do datapath e localiza melhor uma quebra:

```sh
make tb TB=tb_rf_alu
make tb TB=tb_pc_alu
make tb TB=tb_ir_imm
make tb TB=tb_fetch
make tb TB=tb_datapath

make tb TB=tb_branch_pc

make tb TB=tb_lsu_rf
make tb TB=tb_lsu_dmem
make tb TB=tb_memory_bus

make tb TB=tb_mult_rf

make tb TB=tb_core_smoke
make system              # FENCE + ECALL/EBREAK no contrato CMOS
make tb TB=tb_core_faults
make tb TB=tb_memory_faults
make tb TB=tb_isa
make tb TB=tb_firmware
make tb TB=tb_core_crc
make tb TB=tb_simple_system
make official-fetch      # primeira obtenção da revisão fixada
make official-run
```

`tb_isa` é a verificação integrada mais abrangente. `tb_firmware` usa o firmware
próprio e a assinatura `0x600dc0de`; ele não substitui o firmware oficial.

Para executar os 19 testbenches de integração em uma chamada:

```sh
make integration
```

Esse comando requer a toolchain `riscv64-unknown-elf-gcc`, pois inclui
os firmwares próprios. Também requer a imagem oficial em cache, preparada uma
vez por clone com `make official-fetch`.

## 4. Firmware, smoke e waveform

Para executar o firmware próprio no processador baseline:

```bash
make run
cat results/logs/tb_firmware.log
```

O comando compila e simula. `make firmware` somente gera a imagem; `make run`
é equivalente a `make tb TB=tb_firmware` e verifica a assinatura 0x600dc0de.

Antes de uma regressão longa:

```sh
make smoke
```

O smoke executa `tb_core_smoke`, `tb_branch_pc`, `tb_lsu_dmem` e `tb_mult_rf`.

Para gerar a forma de onda do firmware próprio:

```sh
make wave
gtkwave results/waveforms/smoke.vcd
```

## 5. Fechamento da regressão

Antes da primeira execução completa, use `make official-fetch`. A imagem é
fixada por revisão/SHA e fica em cache. `make official-run` verifica apenas o
programa oficial; `make official-wave` também grava seu VCD. O resultado é
x4=0 após a escrita final e o loop, não o zero observado durante reset.

Depois que testes isolados e de integração estiverem PASS:

```sh
make regression
git status --short
```

`make regression` recompõe vetores e firmware, executa os 33 testbenches, roda
lint, atualiza a matriz de cobertura e grava hashes em
`results/logs/regression.json`. Somente esse resultado completo deve ser usado
como evidência de fechamento.

## 6. Experimento simple_system

O sistema com ROM 2 KiB/RAM 1 KiB e Xicrc já existe. Execute:

```bash
make simple-system
```

Esse comando compila o programa experimental e verifica boot, reset, assinatura
e falhas no RTL. Veja [contrato e testes](modules/simple_system.md). O percurso completo é:

1. instanciar o core validado sem alterar suas interfaces;
2. usar ROM e RAM pequenas, dimensionadas somente para um firmware de smoke;
3. expor clock, reset, sinal de sucesso e falha;
4. verificar o mesmo firmware em RTL antes da síntese;
5. após síntese genérica validada, criar configuração LibreLane própria;
6. avançar por floorplan, placement, CTS e routing somente com cada etapa limpa;
7. manter os resultados identificados como experimento, sem alegar M11/M12.

Não se deve sintetizar a IMEM padrão de 4 MiB como registradores. A escolha entre
memória pequena inferida, memória externa ou macro SRAM precisa ser explícita no
contrato do `simple_system`. O top de submissão só deve entrar no fluxo depois de
47/47, firmware oficial e interface física confirmada.

## 7. Síntese lógica e teste da netlist

Depois do sistema RTL aprovado:

```bash
make -n simple-synth
make simple-synth
cat results/logs/simple_netlist.log
python3 -m json.tool results/logs/simple_synth.json
```

Gera `build/simple_netlist.v` com Yosys e simula dois boots nessa netlist.
O resumo deve registrar status/simulação PASS. A execução é adicional aos 33 TBs;
não envolve PDK, timing físico ou GDSII. Tutorial e comandos manuais:
[aula 7](../labs/rtl-to-gds/07-sintese.md); consulta: [synthesis.md](synthesis.md).

## 8. Ambiente físico

Para preparar Docker/imagem, siga [setup.md](setup.md). Depois:

```sh
make setup-openlane
make openlane-env-check
make openlane-env-smoke
```

O smoke executa o circuito de exemplo embutido do LibreLane. Ainda não há
configuração física do simple_system ou do top final; a preparação está na
[aula 8](../labs/rtl-to-gds/08-introducao-openlane.md).
