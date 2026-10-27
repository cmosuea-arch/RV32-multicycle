# Laboratório guiado: do RTL à preparação do fluxo físico

O objetivo é entender e executar o projeto CMOS RISC-V em camadas: bloco isolado,
blocos conectados, core executando programas e automação que registra os resultados.
O exemplo contínuo é a ALU. Primeiro vamos simulá-la manualmente e reconhecer
os mesmos passos nos scripts Python e no Makefile. Em seguida executamos firmware
no core e sintetizamos o sistema pequeno, antes de estudar a preparação física.
A [aula 0 — arquitetura RISC-V](00-arquitetura-riscv.md) fornece a base: papel
dos blocos, conexões do datapath/controle e caminho de uma instrução pelo core.

Para a atividade acompanhada e a preparação do vídeo, comece por
[prática guiada para o vídeo](00-pratica-para-video.md). Usaremos o workspace
atual e avançaremos por etapas conforme você executar. O roteiro começa com uma
[sequência completa de comandos até a síntese lógica](00-pratica-para-video.md#sequência-completa-até-a-síntese-lógica),
incluindo os critérios de avanço e a simulação da netlist. A limpeza é opcional;
o registro de saídas limpas descreve a preparação inicial da prática.

## Percurso

| Ordem | Aula | Ao terminar, você conseguirá… |
|---|---|---|
| 0 | [Arquitetura RISC-V](00-arquitetura-riscv.md) | explicar os blocos, as ligações e a execução multiciclo antes de ler RTL/testes |
| 1 | [Visão geral](01-visao-geral.md) | distinguir circuito, estímulo, referência e ferramenta |
| 2 | [Testes unitários](02-testes-unitarios.md) | gerar vetores, compilar, simular e interpretar uma comparação |
| 3 | [Testes de integração](03-testes-integracao.md) | acompanhar dados entre módulos e programas no core |
| 4 | [Scripts Python](04-scripts-python.md) | seguir a preparação e a execução automática dos testes |
| 5 | [Makefile](05-makefile.md) | explicar alvos, receitas, variáveis e os comandos disponíveis |
| 6 | [Regressão e evidências](06-regressao-e-evidencias.md) | fechar uma rodada e interpretar logs, hashes e cobertura |
| 7 | [Síntese](07-sintese.md) | gerar a netlist com Yosys, simulá-la e interpretar relatórios |
| 8 | [Introdução ao OpenLane](08-introducao-openlane.md) | verificar o ambiente físico e preparar a próxima etapa |

## Preparação

Em máquina nova, siga primeiro [a instalação](../../docs/setup.md):
`bash scripts/setup/install.sh` prepara dependências e `make doctor` confere o ambiente.

Todos os comandos, salvo indicação explícita, são executados **na raiz do projeto**,
inclusive quando você estiver lendo um arquivo dentro desta pasta:

```bash
cd /home/luixf/eda/uniccass-icdesign-tools/shared_xserver/cmos-riscv
pwd
git status --short
make help
make doctor
python3 --version
make --version
iverilog -V
vvp -V
verilator --version
yosys -V
riscv64-unknown-elf-gcc --version
```

Adapte apenas o caminho do `cd` se o clone estiver em outro local. Python 3.9+
é necessário para a API usada pelo executor; o ambiente do projeto usa Python 3.12.
A toolchain RISC-V será necessária para o firmware; GTKWave é opcional para abrir
ondas. Docker com a imagem UNIC-CASS é usado na aula física; basta este clone.
Se uma ferramenta não existir no PATH, resolva o ambiente antes da aula que a utiliza.

## Como estudar

Leia o objetivo, abra os arquivos indicados, faça a previsão do resultado e então
execute os comandos um por vez. Ao aparecer uma falha, leia o log antes de avançar.
As perguntas no final de cada aula possuem respostas para conferência.

`make clean` arquiva build/logs/ondas em `results/archive/`, com hashes. Os logs
anteriores à prática estão em [histórico](../../results/history/pre-guided-20261017/README.md).
Saídas correntes são ignoradas pelo Git; evidências publicadas ficam identificadas
em `results/experiments/`.

Os testes geram ou sobrescrevem arquivos em `build/` e `results/`; a execução
completa também atualiza `docs/isa/coverage.*`. Não execute duas instâncias do
executor ao mesmo tempo: elas compartilham os mesmos caminhos.

Os códigos apresentados são os do repositório, acessíveis pelos links. Não há cópia
didática de RTL para manter sincronizada. Comentários curtos foram adicionados aos
34 testbenches (33 de RTL e um de netlist) e aos blocos usados no percurso.
Não é necessário alterar o código para fazer as práticas.

Para se orientar: `make run` executa o firmware baseline; `make simple-system`
verifica o sistema experimental; `make simple-synth` sintetiza esse sistema e
simula sua netlist. `make help` descreve todos os comandos.

## Alcance

O perfil atual tem **47/47 instruções (100%)**. A regressão atual tem 14 TBs unitários
e 19 de integração, incluindo Xicrc, firmware oficial e simple_system. O teste da netlist
é adicional, executado por `make simple-synth`. FENCE/ECALL/EBREAK passam sob o [EEI CMOS](../../docs/architecture/system.md);
o top físico final tem [pendências registradas](../../docs/architecture/official_questions.md).
O [simple_system](../../docs/modules/simple_system.md) já possui RTL, firmware,
TB e síntese genérica histórica. A configuração física está preparada; a nova execução fica com o usuário.
O smoke test do LibreLane valida o ambiente com um circuito de exemplo.

Comece pela [aula 0](00-arquitetura-riscv.md), depois siga para a
[aula 1](01-visao-geral.md). Para consulta rápida dos comandos, use
o [roteiro operacional](../../docs/testing_roadmap.md).

## Validação deste material

O [guia de leitura](../../docs/code_guide.md) foi incorporado à navegação e os
comentários foram alinhados ao contrato atual. A
[revisão editorial](../../results/experiments/documentation-20261027/README.md)
confirmou receitas/lógica preservadas e 33 TBs/lint PASS em cópia isolada.

A rodada atual registra [33 TBs/lint, 47/47 e firmware oficial PASS](../../results/experiments/isa-47-20261027/README.md).
O registro histórico de 13/10 do sistema experimental aprovou 31 TBs/lint,
síntese genérica e dois boots na netlist: [rodada do simple_system](../../results/experiments/simple/README.md).
O comando `make run` foi validado após a reorganização do Makefile, com assinatura
600dc0de. Na atualização de 2026-10-13, os sete blocos de comandos da aula de
síntese foram executados em cópia isolada: teste RTL, síntese automática,
síntese manual e simulação das duas netlists PASS. Links e prévias dos comandos
Make foram conferidos; os logs locais do usuário foram preservados.

A revisão inicial da navegação das oito aulas foi concluída em 2026-10-15.
Em 27/10 foi acrescentada a aula 0 de arquitetura, totalizando nove aulas, com
as numerações anteriores preservadas. Esse acréscimo é documental; as datas
das execuções acima continuam identificando suas respectivas rodadas.

Registro histórico da primeira versão das aulas:

Em 2026-10-03 foram executados os exemplos manuais de ALU e RF/ALU, as consultas
Python de resultado/codificação, `make wave` e `make regression`: 28 TBs e lint PASS,
com 41/47 preservado. Os links locais foram conferidos. As alterações nos códigos
são somente comentários nessa primeira versão. A prática física se baseia na
instalação e na validação anterior documentadas em [environment.md](../../docs/openlane/environment.md);
o fluxo físico não foi reexecutado para escrever este laboratório.
