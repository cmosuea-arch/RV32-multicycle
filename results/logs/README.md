# Logs da execução atual

Este diretório começa vazio para a prática guiada. Os comandos de teste criam
seus logs aqui; uma regressão completa cria também `regression.json`.
Arquivos gerados são locais e ignorados pelo Git. Evidências de entrega devem
ser copiadas para uma pasta identificada em `results/experiments/`, com manifesto.

Os 65 logs que existiam antes da preparação de 17/10/2026 foram preservados em
[history/pre-guided-20261017](../history/pre-guided-20261017/README.md).
As evidências do relatório continuam em `results/experiments/`.

`make clean` arquiva build, logs e ondas em `results/archive/<data-UTC>/`, com
inventário e hashes; mantém este README, fontes, ambientes fora de build e
evidências publicadas. O backup local é ignorado pelo Git. Para ver a lista
antes: `python3 scripts/setup/clean.py --dry-run`.

Não execute a limpeza enquanto uma simulação, síntese ou exportação estiver
usando esses diretórios. Após limpar, um PASS antigo continua sendo evidência
apenas de sua rodada; o resultado da atividade será produzido por você.
