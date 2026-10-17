# Saídas preservadas antes da prática guiada

Snapshot dos **65 arquivos que estavam em `results/logs/`** em 17/10/2026,
antes da limpeza autorizada pelo usuário. Os bytes foram copiados e conferidos
por SHA-256. [snapshot.json](snapshot.json) registra hashes, commit de referência
e quais logs possuíam modificações locais.

Esta pasta mistura saídas históricas e exercícios individuais posteriores.
Preserva inclusive diagnósticos de compilação e um manifesto antigo; não é
uma nova rodada PASS nem comprovação de que todos esses logs pertencem à mesma
execução. Consulte as datas/comandos e o manifesto de cada evidência.

- [Logs preservados](logs/).
- [Manifesto antigo](logs/regression.json), sem modificar seu conteúdo.
- [Rodada completa identificada do simple_system](../../experiments/simple/README.md).
- [Captura própria usada no relatório](../../experiments/firmware-wave/README.md).

`build/` e o VCD de trabalho, junto com outra cópia dos logs, foram arquivados
localmente por `make clean` em `results/archive/`, com manifesto de integridade.
Esse backup é ignorado pelo Git. RTL, TBs, firmware, relatório e evidências
identificadas não foram removidos.
