# Verificação da versão parcial

Aprendizado passo a passo: [laboratório RTL → fluxo físico](../labs/rtl-to-gds/README.md).

## Reproduzir

```sh
make unit
make integration
make smoke
make regression
make run
make wave
```

O roteiro completo, incluindo execução individual e a ordem incremental, está
em [testing_roadmap.md](testing_roadmap.md).

`make regression` gera os vetores, compila os firmwares próprios, executa 31 TBs e faz
lint. Falhas, timeouts (120 s por processo), qualquer diagnóstico de compilação
e ausência de PASS interrompem o comando com código diferente de zero.
`results/logs/regression.json` registra estado, testbenches, lint e SHA-256 de
RTL, TB, scripts, firmware, Makefile e lista de instruções habilitadas.
Uma execução iniciada sem terminar conserva RUNNING; não é evidência PASS.
`make test` executa os TBs e registra lint como NOT_RUN; use regression para fechar.

## Testes e alcance

| Grupo | Verificação |
|---|---|
| ALU | 18.304 vetores, 11 operações e seletores inválidos |
| RF | escrita de 32 destinos, 1.024 pares de leitura, x0/reset/enable |
| Immediate | 5.102 vetores I/S/B/U/J, bits individuais e aliases de opcode |
| PC/IR/IMEM | retenção, reset, redirects, conteúdo de ROM e sequência de fetch |
| Branch | 9.152 vetores de comparação; tomado/não tomado e alvos negativos no core |
| Decoder | 128 opcodes × 8 funct3 × 128 funct7; controles e rejeição de códigos |
| LSU | 8.960 vetores de byte/half/word, sign/zero extension e desalinhamento |
| DMEM | 256 combinações posição/máscara, read-first, retenção e limites |
| Address Decoder | 768 combinações faixa/pedido/máscara; ROM protegida |
| Multiplicador | 18.304 vetores com signed/mixed/unsigned e partes alta/baixa |
| ISA integrada | 76.409 aposentadorias comparadas em PC, instrução, rd, dado e RF |
| Memória integrada | 45 stores, contagem de escritas físicas e 12 bytes finais |
| Falhas | 12 casos de decode/controle e 12 de memória; efeitos bloqueados e reset |
| Firmware próprio | RV32I_Zmmul/ILP32; ROM/.data/.bss, pilha, chamadas, loops e multiplicação |
| CRC provisório | 18304 vetores, 2127 instruções CRC no core; decoder nos dois perfis |
| simple_system | 7 cenários de boot/reset/assinatura/fault; firmware exercita os três CRCs |

`make simple-synth` é uma checagem adicional, fora da regressão RTL: síntese
genérica Yosys, memória mapeada, ausência de inicialização de registradores e
dois boots do firmware na netlist, observando somente pinos. Logs `simple_synth.*`
e `simple_netlist.*`. Evidências da rodada de referência: `results/experiments/simple/`.
Comandos e interpretação: [síntese](synthesis.md) e
[aula 7](../labs/rtl-to-gds/07-sintese.md).

Vetores determinísticos: seed `0xC005`; programas: seed `4711`. Modelos Python
usam inteiros/bytes para gerar resultados esperados, com codificação das instruções
separada da execução RTL. Firmware compilado pelo GCC adiciona um caminho de
codificação independente dos geradores de testes. A comparação de todas as
aposentadorias inclui instruções auxiliares que preparam os operandos.

Lint Verilator: Wall ativo. Suprimidos apenas DECLFILENAME (nomes de arquivos),
UNUSEDSIGNAL/UNUSEDPARAM (interfaces e bits reservados). `riscv_top` e
`simple_system` são elaborados separadamente, verificando as duas configurações
de memórias/CRC. Nenhuma supressão de latch, largura ou loop combinacional.

## Evidências

- `results/logs/tb_*.compile.log`: comandos e compilação limpa.
- `results/logs/tb_*.log`: verificações PASS.
- `results/logs/firmware_build.log` e `smoke.disasm`: compilação e instruções emitidas.
- `results/logs/lint.log`: comando de lint; sem diagnósticos significa sucesso.
- `results/logs/regression.json`: resultado agregado com hashes.
- `results/logs/simple_synth.json` e `simple_netlist.log`: rodada de síntese genérica,
  produzida separadamente por `make simple-synth`.
- `results/waveforms/smoke.vcd`: waveform reproduzível por `make wave`, ignorada
  pelo Git para evitar arquivos grandes; o log da execução com waveform é versionado.

## Limitações

São testes funcionais, não prova formal, cobertura de todos os valores de entrada
ou certificação. Firmware oficial ainda não foi executado. FAULT é diagnóstico
CMOS até reset; não implementa ambiente privilegiado/traps/CSRs. Lint não prova
que as memórias inferidas cabem fisicamente no chip. Nenhum resultado de área,
timing, OpenLane ou GDSII do processador é alegado nesta versão. A contagem de
células genéricas da síntese experimental não é área física nem fechamento.
