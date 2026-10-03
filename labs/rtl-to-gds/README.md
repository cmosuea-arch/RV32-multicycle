# Laboratório guiado: do RTL à preparação do fluxo físico

O objetivo é entender e executar o projeto CMOS RISC-V em camadas: bloco isolado,
blocos conectados, core executando programas e automação que registra os resultados.
O exemplo contínuo é a ALU. Primeiro vamos simulá-la manualmente; depois reconhecer
os mesmos passos nos scripts Python e no Makefile.

## Percurso

| Ordem | Aula | Ao terminar, você conseguirá… |
|---|---|---|
| 1 | [Visão geral](01-visao-geral.md) | distinguir circuito, estímulo, referência e ferramenta |
| 2 | [Testes unitários](02-testes-unitarios.md) | gerar vetores, compilar, simular e interpretar uma comparação |
| 3 | [Testes de integração](03-testes-integracao.md) | acompanhar dados entre módulos e programas no core |
| 4 | [Scripts Python](04-scripts-python.md) | seguir a preparação e a execução automática dos testes |
| 5 | [Makefile](05-makefile.md) | explicar alvos, receitas, variáveis e os comandos disponíveis |
| 6 | [Regressão e evidências](06-regressao-e-evidencias.md) | fechar uma rodada e interpretar logs, hashes e cobertura |
| 7 | [Introdução ao OpenLane](07-introducao-openlane.md) | verificar o ambiente físico e planejar o simple_system |

## Preparação

Todos os comandos, salvo indicação explícita, são executados **na raiz do projeto**,
inclusive quando você estiver lendo um arquivo dentro desta pasta:

```bash
cd /home/luixf/eda/uniccass-icdesign-tools/shared_xserver/cmos-riscv
pwd
git status --short
python3 --version
make --version
iverilog -V
vvp -V
verilator --version
riscv64-unknown-elf-gcc --version
```

Adapte apenas o caminho do `cd` se o clone estiver em outro local. Python 3.9+
é necessário para a API usada pelo executor; o ambiente do projeto usa Python 3.12.
A toolchain RISC-V será necessária para o firmware; GTKWave é opcional para abrir
ondas. Docker com a imagem e o workspace UNIC-CASS é usado na aula física.
Se uma ferramenta não existir no PATH, resolva o ambiente antes da aula que a utiliza.

## Como estudar

Leia o objetivo, abra os arquivos indicados, faça a previsão do resultado e então
execute os comandos um por vez. Ao aparecer uma falha, leia o log antes de avançar.
As perguntas no final de cada aula possuem respostas para conferência.

Os testes geram ou sobrescrevem arquivos em `build/` e `results/`; a execução
completa também atualiza `docs/isa/coverage.*`. Não execute duas instâncias do
executor ao mesmo tempo: elas compartilham os mesmos caminhos.

Os códigos apresentados são os do repositório, acessíveis pelos links. Não há cópia
didática de RTL para manter sincronizada. Comentários curtos foram adicionados aos
blocos usados no percurso; não é necessário alterar o código para fazer as práticas.

## Alcance

A baseline tem **41/47 instruções (87,23%)**, 13 TBs unitários e 15 de integração.
Os números esperados das aulas se referem a essa versão. CRC, sistema/sincronização,
firmware oficial e top físico final têm [pendências registradas](../../docs/architecture/official_questions.md).
O `simple_system` é uma próxima etapa planejada; este laboratório ainda não contém
seu RTL ou configuração física. O smoke test do LibreLane valida o ambiente com
um circuito de exemplo.

Comece pela [aula 1](01-visao-geral.md). Para consulta rápida dos comandos, use
o [roteiro operacional](../../docs/testing_roadmap.md).

## Validação deste material

Em 2026-10-03 foram executados os exemplos manuais de ALU e RF/ALU, as consultas
Python de resultado/codificação, `make wave` e `make regression`: 28 TBs e lint PASS,
com 41/47 preservado. Os links locais foram conferidos. As alterações nos códigos
são somente comentários. A prática física se baseia na instalação e na validação
anterior documentadas em [environment.md](../../docs/openlane/environment.md);
o fluxo físico não foi reexecutado para escrever este laboratório.
