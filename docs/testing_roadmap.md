# Roteiro de testes do RTL

Este roteiro valida o subconjunto atual de 41/47 instruções em camadas. CRC,
sistema/sincronização e firmware oficial continuam pendentes e não são contados
como PASS.

## 1. Preparação

Execute na raiz do repositório:

```sh
cd /home/luixf/eda/uniccass-icdesign-tools/shared_xserver/cmos-riscv
git status --short
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
```

Para executar os 13 testbenches unitários em uma chamada:

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
make tb TB=tb_core_faults
make tb TB=tb_memory_faults
make tb TB=tb_isa
make tb TB=tb_firmware
```

`tb_isa` é a verificação integrada mais abrangente. `tb_firmware` usa o firmware
próprio e a assinatura `0x600dc0de`; ele não substitui o firmware oficial.

Para executar os 15 testbenches de integração em uma chamada:

```sh
make integration
```

Esse comando requer a toolchain `riscv64-unknown-elf-gcc`, pois inclui
`tb_firmware`.

## 4. Smoke e waveform

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

Depois que testes isolados e de integração estiverem PASS:

```sh
make regression
git status --short
```

`make regression` recompõe vetores e firmware, executa os 28 testbenches, roda
lint, atualiza a matriz de cobertura e grava hashes em
`results/logs/regression.json`. Somente esse resultado completo deve ser usado
como evidência de fechamento.

## 6. Ambiente físico

Enquanto o RTL final da competição permanece pendente, valide apenas a
infraestrutura LibreLane:

```sh
make openlane-env-check
make openlane-env-smoke
```

O segundo comando usa o circuito de exemplo embutido do LibreLane e não executa
o processador.

## 7. Próximo experimento: simple_system

Depois de uma regressão PASS, o próximo exercício físico pode ser um top
`simple_system` separado do `riscv_top` final. A proposta é:

1. instanciar o core validado sem alterar suas interfaces;
2. usar ROM e RAM pequenas, dimensionadas somente para um firmware de smoke;
3. expor clock, reset, sinal de sucesso e falha;
4. verificar o mesmo firmware em RTL antes da síntese;
5. criar configuração LibreLane própria e executar primeiro até síntese;
6. avançar por floorplan, placement, CTS e routing somente com cada etapa limpa;
7. manter os resultados identificados como experimento, sem alegar M11/M12.

Não se deve sintetizar a IMEM padrão de 4 MiB como registradores. A escolha entre
memória pequena inferida, memória externa ou macro SRAM precisa ser explícita no
contrato do `simple_system`. O top de submissão só deve entrar no fluxo depois de
47/47, firmware oficial e interface física confirmada.
