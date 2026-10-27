# Prática guiada para entender o sistema e preparar o vídeo

[Índice das aulas](README.md) · [Base: arquitetura RISC-V](00-arquitetura-riscv.md) · [Aula 1](01-visao-geral.md)

Vamos usar **este workspace e a branch atual**. A prática começa com saídas
limpas e avança conforme você executa e explica cada etapa. O objetivo é
conseguir narrar o percurso do RTL até as evidências de implementação.
As aulas existentes são a referência detalhada; esta página organiza as sessões.

## Sequência completa até a síntese lógica

Execute na raiz do projeto, um comando por vez. A tabela é o roteiro de execução;
as sessões abaixo e as aulas explicam os arquivos e cada comparação.

| Ordem | Execução | Resultado necessário para avançar |
|---|---|---|
| 0 | Leitura da [aula de arquitetura](00-arquitetura-riscv.md), sem comandos obrigatórios | Explicar PC/IR/RF, datapath/controle e o caminho de ADD, load/store e branch |
| 1 | `make doctor` | Ferramentas e compilação RV32I_Zmmul/ILP32 disponíveis; instalação em máquina nova conforme [setup](../../docs/setup.md) |
| 2 | Prática manual da [aula 2](02-testes-unitarios.md), depois `make tb TB=tb_alu` | ALU/TB/vetores compreendidos; simulação manual e automatizada PASS |
| 3 | `make unit` | 14 testbenches dos blocos isolados PASS |
| 4 | `make official-fetch` | Imagem oficial da revisão fixada verificada e preparada; uma vez por clone |
| 5 | Práticas da [aula 3](03-testes-integracao.md), depois `make integration` | 19 integrações PASS: blocos conectados, core, memória, CRC, sistema e firmwares |
| 6 | `make system` | Entender FENCE e os traps ECALL/EBREAK, sem confundir trap com aposentadoria |
| 7 | `make run`, depois `make wave` | Firmware próprio até a assinatura; identificar boot/execução/término no VCD |
| 8 | `make official-run`, depois `make official-wave` | Firmware oficial até x4 final e loop; log/VCD da própria execução |
| 9 | `make regression` | 33 TBs e lint PASS; manifesto da rodada e cobertura 47/47 sob o EEI CMOS |
| 10 | `make simple-system` | Sistema reduzido e firmware que serão usados na síntese passam em RTL |
| 11 | `make -n simple-synth`, depois `make simple-synth` | ROM recompilada, síntese Yosys e dois boots da netlist PASS |
| 12 | Ler `build/simple_netlist.v`, `results/logs/simple_synth.log`, `simple_netlist.log` e `simple_synth.json` | Localizar circuito gerado, checagens, contagem de células e hashes |

A leitura das [aulas 4](04-scripts-python.md) e [5](05-makefile.md) acompanha os
comandos: descubra qual receita chama o script e quais arquivos ele produz.
Na [aula 6](06-regressao-e-evidencias.md), confira as evidências antes de seguir
para a [aula 7](07-sintese.md), que também apresenta a síntese manual equivalente.

O ponto de chegada desta sequência é **síntese lógica genérica com netlist
simulada**. Mapeamento SKY130A, implementação física e signoff seguem na
[aula 8](08-introducao-openlane.md) e exigem os resultados da sua execução.
Este roteiro não executa síntese por conta própria; essa etapa permanece com você.

## Como conduzir cada sessão

1. Abra os arquivos indicados e explique a função de cada um.
2. Preveja qual arquivo/comando deve produzir o próximo resultado.
3. Execute um comando por vez e leia o primeiro erro ou o PASS.
4. Localize a comparação ou verificação que justifica o resultado.
5. Faça uma explicação de 30–60 segundos com suas próprias palavras.

Comece pela etapa 1. Só avance quando souber explicar o resultado e onde ele
foi registrado. Não é necessário gravar todas as sessões; elas preparam uma
apresentação final de 5–7 minutos.

## Histórico da preparação do workspace

`build/` foi arquivado e os logs/ondas de trabalho foram retirados dos diretórios
de execução. Os arquivos antigos ficam no
[histórico de preparação](../../results/history/pre-guided-20261017/README.md).
As evidências usadas pelo relatório permanecem em `results/experiments/`.
Nenhum teste da nova prática foi executado durante essa preparação.
Esse registro é da limpeza inicial em 17/10. Houve validações posteriores,
identificadas em `results/experiments/`; confira o estado atual antes de decidir
reiniciar a prática. A seção final explica a limpeza opcional.

| Local | Papel durante a atividade |
|---|---|
| `rtl/`, `tb/`, `scripts/`, `firmware/` | Fontes que explicam e reproduzem o sistema |
| `build/` | Produtos que você verá nascer: vetores, ROM, executáveis e netlist |
| `results/logs/` | Comandos e resultados da sua execução atual |
| `results/waveforms/` | VCD novo quando você executar `make wave` |
| `results/experiments/` | Evidências identificadas das rodadas já publicadas |
| `results/archive/` | Backups locais produzidos por `make clean`; ignorados pelo Git |

As saídas correntes são ignoradas pelo Git. Para uma entrega, é preciso separar
uma rodada identificada em `results/experiments/`, com logs e manifesto que
correspondam aos mesmos arquivos testados. O material histórico não representa
um PASS novo de sua atividade.

## Etapa 1 — Mapa dos arquivos e ambiente

Antes de executar, faça a [aula 0 — arquitetura RISC-V](00-arquitetura-riscv.md).
Desenhe o caminho de uma ADD e diferencie núcleo, memórias e controle. Essa é
a base para interpretar os testes das próximas sessões.

Abra [Makefile](../../Makefile), [alu.sv](../../rtl/alu.sv),
[tb_alu.sv](../../tb/unit/tb_alu.sv), [vectors.py](../../scripts/sim/vectors.py)
e [run.py](../../scripts/regression/run.py). Consulte a [aula 1](01-visao-geral.md).
Execute na raiz:

```bash
pwd
git status --short
make help
make doctor
make -n tb TB=tb_alu
```

`doctor` verifica ferramentas e compila apenas uma pequena prova de suporte
RV32I_Zmmul em diretório temporário. `-n` mostra a receita sem executar o teste.
`build/` ainda não precisa aparecer.

**Explique:** qual arquivo descreve o hardware, qual fornece estímulos, qual
calcula o esperado e qual inicia as ferramentas? O que o Makefile delega ao Python?

**Critério:** reconhecer os cinco arquivos e obter o diagnóstico do ambiente.

## Etapa 2 — ALU manual e automatizada

Siga a [aula 2](02-testes-unitarios.md): gere os vetores, compile apenas ALU/TB
com Icarus e execute com vvp. Depois compare com `make tb TB=tb_alu`.
Veja o conteúdo de `build/alu.vec` e os dois logs da bancada.

**Explique:** de onde vem o resultado esperado, quando o RTL calcula sua saída
e onde o TB compara? O que exatamente significa PASS? Por que compilar e simular
são passos distintos?

O executor pode preparar arquivos auxiliares para outras bancadas; `-s tb_alu`
seleciona apenas a ALU. A existência de um arquivo ISA em build não significa
que o teste ISA já foi executado.

**Critério:** os dois caminhos aprovam e você identifica um vetor e sua comparação.

## Etapa 3 — Demais blocos e integrações

Continue as [aulas 2 e 3](03-testes-integracao.md), seguindo a ordem incremental.
RF/ALU mostra leitura, cálculo e escrita; PC/IMEM/IR mostra fetch. Depois entram
controle de fluxo, LSU/memória, multiplicação, core e testes de falhas.

**Explique:** o que um teste isolado deixa de observar e o teste conectado passa
a verificar? Em qual borda os registradores mudam? Por que load/store têm um
estado adicional? Como a FSM controla os enables?

**Critério:** testes selecionados PASS e caminho de uma instrução descrito no datapath.

## Etapa 4 — Python, Make e regressão

Siga as [aulas 4](04-scripts-python.md), [5](05-makefile.md) e
[6](06-regressao-e-evidencias.md). Relacione as receitas ao executor e execute
`make regression` quando os testes específicos estiverem compreendidos.
Antes da primeira rodada que inclui o firmware oficial, execute `make official-fetch`.
O download é explícito e validado por SHA-256; as execuções seguintes usam o cache.

**Explique:** como sementes fixas permitem reproduzir entradas? Como uma falha
retorna ao terminal? O que muda entre teste individual, suíte e regressão completa?
Qual é o papel dos hashes e da cobertura por instrução?

**Critério:** 33 TBs e lint PASS na configuração atual, manifesto da sua rodada
com estado PASS e cobertura **47/47** no EEI CMOS. Use `make system` para
explicar FENCE e os traps de ECALL/EBREAK; estes não aposentam.

## Etapa 5 — Firmware no processador e waveform

Use `make run` e depois `make wave`, conforme a
[aula 3](03-testes-integracao.md). Leia `start.S`, `main.c`, `link.ld`,
o gerador de ROM e `tb_firmware.sv`. Observe no VCD o boot e a escrita final.

**Explique:** GCC transforma C/assembly em instruções RISC-V; o core busca essas
instruções na ROM. Startup prepara pilha/dados, main executa verificações e o TB
observa a assinatura na RAM. Onde estão PC, instrução, estado, endereço e dado
na escrita de `0x600dc0de`?

**Critério:** assinatura correta no log e na memória; interpretação de sua própria
captura. Depois execute `make official-run` e `make official-wave`: o programa
oficial já está integrado e usa escrita final de x4=0 seguida de três commits do
loop, em vez da assinatura na DMEM. Ele exercita 44 tipos; os testes próprios
de sistema completam o perfil de 47.

## Etapa 6 — simple_system, síntese e netlist

Siga a [aula 7](07-sintese.md): `make simple-system`, depois `make simple-synth`.
Identifique memórias reduzidas, Xicrc e saídas de resultado. Inspecione
a netlist, o resumo Yosys e o teste de dois boots.

**Explique:** qual circuito foi sintetizado? Como o firmware foi incorporado à ROM?
Por que o teste da netlist é necessário? O que a contagem de células genéricas
permite afirmar e quais resultados dependem do PDK/fluxo físico?

**Critério:** RTL e netlist PASS, sabendo que mudar o firmware embutido exige
ressíntese nesse experimento.

## Etapa 7 — Fluxo físico e fechamento futuro

A [aula 8](08-introducao-openlane.md) verifica ferramentas/PDK e explica o
percurso físico. O exemplo LibreLane valida o ambiente. A configuração/restrições
do `simple_system` estão [preparadas para sua execução](../../openlane/simple_system/README.md).
Ainda precisamos da rodada física do projeto, interface final, diagramas e
resultados revisados para fechar a submissão. O firmware oficial já passou em RTL.
Em 20/10, a execução da síntese ficou reservada
ao usuário; estudar as receitas com `make -n` não inicia as ferramentas.

**Explique, quando os resultados existirem:** mapeamento, floorplan, placement,
CTS, roteamento, área/densidade, timing, DRC/LVS e GDSII. Identifique o top,
commit e configuração da execução que está mostrando.

**Critério futuro:** resultados do próprio projeto revisados e incorporados ao
relatório. A prática atual pode avançar até as etapas disponíveis; preparação
para signoff requer implementação física e análise de seus relatórios.

## Roteiro da gravação final — aproximadamente 6 minutos

| Tempo | Conteúdo | Evidência na tela |
|---|---|---|
| 0:00–0:40 | Objetivo, arquitetura multiciclo e escopo | Diagrama geral e cobertura atualizada |
| 0:40–1:30 | Caminho de uma instrução e controle | Datapath/FSM, PC, RF e memória |
| 1:30–2:30 | Como o projeto foi verificado | ALU/TB/vetor, PASS e manifesto da regressão |
| 2:30–3:40 | Simulação e execução do firmware | Startup/main, waveform e assinatura/log final |
| 3:40–4:30 | Síntese e verificação da netlist | Configuração, netlist e log da rodada |
| 4:30–5:40 | Resultados OpenLane e layout final | Área/densidade, verificações e imagem do GDSII |
| 5:40–6:00 | Identificação da entrega | Commit, arquivos e conclusão efetivamente comprovada |

Essa é a estrutura do vídeo de entrega, que será completada com os resultados
físicos quando disponíveis. Você já pode ensaiar os trechos de arquitetura,
verificação e ambos os firmwares. O guia exige vídeo de 5–7 minutos
no YouTube cobrindo arquitetura, funcionamento, simulação, firmware, OpenLane e
layout. Use trechos preparados de execução e imagens legíveis para manter o tempo.

## Reiniciar uma prática

```bash
python3 scripts/setup/clean.py --dry-run
make clean
```

O comando move saídas para um backup local com inventário e hashes. Fontes,
`.venv` da raiz, evidências publicadas e relatório permanecem. Um ambiente de
exportação instalado dentro de build também é arquivado e precisará ser recriado.
Execute a limpeza com os processos de teste/síntese encerrados.
