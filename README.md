# CMOS RISC-V — ChampionCHIP

Processador RISC-V de 32 bits, multiciclo, desenvolvido incrementalmente para a
Fase 2 da ChampionCHIP. Este repositório reúne RTL, testbenches autoverificáveis,
firmware próprio, automação Python/Make e documentação arquitetural.

**Baseline: 41/47 instruções (87,23%)**, com 14 testbenches unitários e 17 de
integração na regressão atual. Há também três instruções CRC sob um
[contrato provisório CMOS](docs/architecture/crc_provisional.md), habilitado
no `simple_system`, com firmware próprio e síntese lógica genérica. Confirmação
oficial do CRC, sistema/sincronização, firmware oficial e interface física final
continuam pendentes. O projeto completo ainda
não está concluído. Consulte [o estado detalhado](docs/status.md) e
[as definições oficiais necessárias](docs/architecture/official_questions.md).

O [relatório técnico da Fase 2](docs/report/README.md) já possui redação inicial
e prévia PDF, organizadas conforme o guia da competição. A
[lista de conferência](docs/report/conformidade.md) identifica os requisitos e
as figuras/resultados ainda necessários para a submissão.

## Comece pelo laboratório

O [laboratório guiado RTL → fluxo físico](labs/rtl-to-gds/README.md) ensina a
executar e entender este projeto. Ele usa os arquivos reais, com comentários
sucintos nos blocos de código que acompanham as explicações.

| Aula | Tema |
|---|---|
| [1 — Visão geral](labs/rtl-to-gds/01-visao-geral.md) | circuito, testbench, referência e ferramentas |
| [2 — Testes unitários](labs/rtl-to-gds/02-testes-unitarios.md) | ALU manual com Icarus/vvp e demais blocos |
| [3 — Integração](labs/rtl-to-gds/03-testes-integracao.md) | conexões, core, ISA e firmware próprio |
| [4 — Python](labs/rtl-to-gds/04-scripts-python.md) | geração de vetores, modelos e executor |
| [5 — Makefile](labs/rtl-to-gds/05-makefile.md) | construção das receitas e comandos do terminal |
| [6 — Regressão](labs/rtl-to-gds/06-regressao-e-evidencias.md) | logs, hashes, cobertura e critérios de sucesso |
| [7 — Síntese](labs/rtl-to-gds/07-sintese.md) | Yosys, netlist genérica, simulação e relatórios |
| [8 — OpenLane](labs/rtl-to-gds/08-introducao-openlane.md) | ambiente LibreLane e preparação física |

Cada aula apresenta objetivo, arquivos, explicação, execução, resultados esperados
e um exercício com critério de avanço. Execute os comandos na raiz do projeto,
um de cada vez. Para consulta rápida, use [o roteiro operacional](docs/testing_roadmap.md).

## Arquitetura e escopo

A referência é o Block Guide ChampionCHIP. O projeto busca RV32I, Zmmul e Xicrc;
a implementação atual cobre aritmética, lógica, imediatos, branches, jumps,
loads/stores e as quatro multiplicações. O Ibex é apenas uma possível referência
auxiliar; o RTL do projeto não incorpora o core Ibex.

O caminho básico é `FETCH → DECODE → EXECUTE → WRITEBACK`. Loads/stores acrescentam
o estado `MEMORY`; erros não suportados levam ao diagnóstico `FAULT` até reset.
O clock usa borda de subida e o reset é síncrono, ativo alto.

`riscv_core` reúne datapath e controle e expõe o barramento de memória.
`riscv_top` liga o core ao decodificador de endereços, IMEM e DMEM. Sinais `commit_*`
permitem verificar instruções aposentadas; ainda não representam a pinagem final.

| Memória | Base | Capacidade padrão |
|---|---|---|
| IMEM | `0x00400000` | 4 MiB |
| DMEM | `0x10010000` | 8 KiB |

Os TBs podem parametrizar memórias menores. Os modelos comportamentais precisam de
uma estratégia própria para implementação física. Detalhes:
[diagrama](docs/architecture/block_diagram.md),
[interfaces](docs/architecture/interfaces.md),
[mapa de memória](docs/architecture/memory_map.md) e
[decisões](docs/architecture/decisions.md).

## Executar

Para um clone novo em Ubuntu 24.04 ou WSL2:

```bash
git clone https://github.com/cmosuea-arch/RV32-multicycle.git
cd RV32-multicycle
bash scripts/setup/install.sh
make doctor
make regression
```

O instalador prepara os pacotes do sistema e `.venv`. O `requirements.txt` registra
que os scripts de simulação/regressão usam apenas a biblioteca padrão de Python.
A exportação opcional do relatório tem [dependências separadas](docs/report/README.md).
Atualização:
`make update` para dependências, ou `bash scripts/setup/update.sh --pull` para
incluir o código remoto (checkout limpo e fast-forward). Veja
[instalação, opções e diagnóstico](docs/setup.md).

Para simulação: Python 3.9+ (3.12 no ambiente usado), Make, Icarus Verilog
(`iverilog`/`vvp`) e Verilator. O firmware usa GCC/binutils
`riscv64-unknown-elf-*`, configurados para `rv32i_zmmul`/`ilp32`.
GTKWave é opcional. O ambiente físico usa Docker e a instalação UNIC-CASS;
veja [os requisitos e caminhos](docs/openlane/environment.md).

```sh
# Executar na raiz do repositório.
make help              # lista comandos e suas finalidades
make tb TB=tb_alu       # uma bancada, com preparação das entradas
make unit              # 14 testbenches unitários, incluindo CRC provisório
make integration       # 17 integrações, incluindo CRC e simple_system
make smoke             # quatro integrações rápidas, sem GCC RISC-V
make lint              # análise estática com Verilator
make test              # todos os TBs; manifesto registra lint NOT_RUN
make regression        # todos os TBs + lint + cobertura + manifesto
make firmware          # somente compila o firmware próprio e gera a ROM
make run               # compila e executa o firmware próprio no processador simulado
make wave              # executa firmware no RTL e gera VCD
make simple-system     # sistema experimental com firmware e CRC provisório
make simple-synth      # síntese Yosys e teste da netlist genérica
```

Para executar o processador com nosso firmware, use `make run`; para acompanhar
seus sinais, use `make wave`. `make firmware` apenas compila o programa.

Para sintetizar o sistema experimental, siga a [aula de síntese](labs/rtl-to-gds/07-sintese.md)
ou a [consulta rápida](docs/synthesis.md). `make simple-synth` gera a netlist e a
testa com o firmware; o fluxo físico completo do sistema ainda é uma etapa futura.

`make -n tb TB=tb_alu` mostra a receita sem executá-la. `make` sem alvo chama
`test`; para fechar uma alteração use `make regression`. Não execute essas receitas
em paralelo: elas compartilham vetores, programas e logs.

O Makefile chama o executor Python. O executor gera entradas, chama `iverilog` para
compilar/elaborar, `vvp` para simular e Verilator para lint. O testbench compara o
RTL com referências e produz PASS ou erro; o Python registra e propaga esse resultado.

## Verificação e firmware

Uma regressão completa deve terminar com **31 TBs PASS e lint PASS** na versão
atual. O teste ISA compara 76.409 aposentadorias, 45 stores e 12 bytes finais com
o modelo Python. O firmware próprio escreve `0x600dc0de` em `0x10011ff0`; sua
baseline executa 598 aposentadorias em 2.579 ciclos.

O programa em [firmware/smoke/](firmware/smoke/README.md) usa C, startup assembly
e linker script. Ele valida boot, dados, pilha, controle e cálculos, mas não fecha
o entregável do [firmware oficial](firmware/official/README.md).

| Evidência | Onde consultar |
|---|---|
| Comandos e resultados de cada TB | `results/logs/tb_*.compile.log` e `tb_*.log` |
| Resultado agregado e hashes da rodada | [regression.json](results/logs/regression.json) |
| Matriz por instrução | [Markdown](docs/isa/coverage.md), [CSV](docs/isa/coverage.csv), [Excel](docs/isa/coverage.xlsx) |
| Alcance e limitações dos testes | [verification.md](docs/verification.md) |
| Forma de onda do firmware | `results/waveforms/smoke.vcd`, gerada por `make wave` |

`build/` contém artefatos recriáveis. Rodadas sobrescrevem logs e a execução completa
atualiza a cobertura. Um PASS anterior só caracteriza os arquivos daquela rodada;
após alterações, gere nova evidência. A matriz registra instruções verificadas,
não prova formal nem cobertura exaustiva de todos os estados do circuito.

## Organização

```text
cmos-riscv/
├── AGENTS.md               # critérios e ordem de desenvolvimento
├── Makefile                # receitas de teste e ambiente físico
├── rtl/                    # blocos, core e top de integração
├── tb/
│   ├── unit/               # módulos isolados
│   └── integration/        # conexões, core e firmware
├── scripts/
│   ├── sim/                # modelos, vetores, programas e build do firmware
│   ├── regression/         # executor e publicação da cobertura
│   ├── synth/              # síntese Yosys e teste da netlist genérica
│   └── openlane/           # acesso ao ambiente Docker
├── firmware/               # smoke próprio e pendência do firmware oficial
├── docs/                   # arquitetura, módulos, ISA, estado e ambiente
├── labs/rtl-to-gds/         # percurso didático
├── build/                  # temporários gerados, ignorados pelo Git
└── results/                # logs, evidências e waveforms
```

## OpenLane/LibreLane: ambiente disponível

A imagem UNIC-CASS `isaiassh/unic-cass-tools:1.1.0` contém LibreLane e SKY130A.
A validação registrada em 2026-09-15 executou o smoke embutido até GDSII, com DRC,
LVS e antena PASS. Consulte [o registro](results/openlane/environment-smoke.md).

```bash
make openlane-env-check     # ferramentas e PDKs
make openlane-env-smoke     # circuito de exemplo até o fim do fluxo físico
make openlane-shell        # terminal interativo dentro do contêiner
```

Com Docker disponível, `make setup-openlane` baixa a imagem e verifica ferramentas
e PDK. O wrapper e o verificador estão neste clone, sem dependência do diretório pai.
O smoke usa
arquivos temporários no contêiner, descartados ao sair. Ainda não há GDSII do
processador nem configuração física final. O `simple_system` já possui RTL,
firmware, testbench e síntese genérica; ainda não há configuração OpenLane dele.

## Próximos passos

O [simple_system](docs/modules/simple_system.md) executa firmware próprio em ROM
de 2 KiB e RAM de 1 KiB, com saídas done/success/fault. O CRC provisório é opt-in
no core e ativo nesse experimento. Consulte a [matriz experimental](docs/isa/experimental_crc.md)
e as [evidências](results/experiments/simple/README.md).

O próximo passo experimental é preparar restrições e configuração física,
avaliar área/timing e a estratégia de memórias em SKY130A. A síntese genérica
e seu teste não substituem essas etapas. Veja o percurso na
[aula 8](labs/rtl-to-gds/08-introducao-openlane.md).

A conclusão do processador da competição mantém outra lista de requisitos:
confirmar o algoritmo Xicrc e adaptar a implementação, se necessário, até
44/47 oficiais; confirmar as três instruções de sistema/sincronização até 47/47; validar
o firmware oficial; fechar interface e top físico; congelar/taguear RTL e executar
o fluxo final conforme [AGENTS.md](AGENTS.md). Diagramas ChipInventor, fechamento
do relatório preliminar e vídeo também permanecem entregáveis pendentes.
