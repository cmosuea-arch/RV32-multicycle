# 6 — Regressão, logs e cobertura

[Anterior](05-makefile.md) · [Índice](README.md) · [Próxima](07-sintese.md)

## Objetivo e arquivos

Verificar se o conjunto continua funcionando e identificar exatamente a versão
testada. Use [run.py](../../scripts/regression/run.py),
[coverage.py](../../scripts/regression/coverage.py) e
[verification.md](../../docs/verification.md).

## Execute a rodada de fechamento

```bash
make smoke
make official-fetch  # uma vez por clone; depois o cache permite regressão offline
make regression
python3 -m json.tool results/logs/regression.json
git status --short
```

O smoke deve informar quatro bancadas aprovadas. A regressão completa deve informar
33 testbenches, lint PASS, firmware próprio com assinatura `600dc0de` e cobertura
47/47. Se qualquer etapa falhar, investigue antes de aceitar a rodada.

## Leia as evidências

| Arquivo | O que responde |
|---|---|
| `tb_alu.compile.log` | qual comando compilou a bancada e houve diagnóstico? |
| `tb_alu.log` | quantos vetores foram comparados e houve diferença? |
| `tb_isa.log` | o trace arquitetural e a memória final coincidiram? |
| `firmware_build.log` | quais flags compilaram o firmware e qual seu tamanho? |
| `tb_firmware.log` | o core realmente executou até a assinatura? |
| `tb_core_crc.log` | as instruções Xicrc coincidiram com o trace? |
| `tb_official_firmware.log` | o programa oficial chegou à escrita final de x4 e ao loop? |
| `tb_simple_system.log` | sistema pequeno passou nos cenários de boot/reset/falha? |
| `lint.log` | qual análise estática foi executada? |
| `regression.json` | quais testes, status, horário e hashes formam a rodada? |

Todos ficam em `results/logs/`, gerados pela sua execução e ignorados pelo Git.
O diretório começa sem resultados depois da limpeza; rodadas anteriores estão
no histórico ou em `results/experiments/`. Um log de lint bem-sucedido ainda tem a linha do
comando; o que deve estar ausente são diagnósticos da ferramenta. `lint.log`
reúne as duas chamadas, também salvas em `lint_riscv_top.log` e `lint_simple_system.log`.

O manifesto recebe `RUNNING` no início, `PASS` no fechamento ou `FAIL` nas falhas
tratadas pelo executor. Uma interrupção pode deixar `RUNNING`. A seção `sha256`
identifica o conteúdo dos arquivos daquela rodada; após editar fontes, execute a
regressão de novo. Mesmo um comentário muda o hash.

Testes individuais e suítes parciais sobrescrevem seus logs, mas não publicam um novo
manifesto de sucesso completo. Portanto, o manifesto anterior não comprova alterações
posteriores. `make test` publica uma rodada completa com lint `NOT_RUN`; para fechar
o projeto com lint use `make regression`.

## Como a cobertura é publicada

```text
enabled.json → programs.py → trace esperado + contagens
                              ↓
                  tb_isa compara com o RTL
                              ↓
             todos os TBs selecionados aprovados
                              ↓
                coverage.py → CSV → Markdown/Excel
```

`coverage.py` verifica se as instruções habilitadas aparecem nas contagens do modelo
e atribui os estados usando a lista habilitada e o sucesso do fluxo que o chamou.
Ele não reexecuta testes nem analisa individualmente cada log. A matriz é uma
rastreabilidade do subconjunto testado; não é cobertura automática de linhas,
branches ou todos os valores possíveis do RTL.

Não rode a geração de cobertura diretamente para certificar uma alteração. Para
reformatar uma matriz já registrada, sem alegar nova execução, existe:

```bash
python3 scripts/regression/coverage.py --render-only
```

Essa opção lê o CSV existente e recria Markdown/Excel. A tag `isa-41-v1` identifica
o marco RTL da matriz atual; hashes e horário no manifesto identificam a rodada.
O firmware oficial só recebe PASS quando tb_official_firmware conclui a imagem
publicada. O firmware próprio, sozinho, não altera esse estado.

## Evidências de síntese são outra rodada

Na próxima aula, `make simple-synth` produz `simple_synth.log`, `simple_netlist.log`
e o resumo `simple_synth.json`. Esses arquivos verificam estrutura sintetizada e
dois boots na netlist. Não publicam cobertura de ISA nem substituem a regressão RTL.

O contrato CRC oficial foi incorporado ao perfil de 44 instruções. O firmware
oficial também é executado com detecção do término real em x4. Consulte a
[rodada de 27/10](../../results/experiments/crc-official-20261027/README.md)
para distinguir a evidência identificada dos logs de exercícios posteriores.

## Se algo falhar

Retorne ao teste mais específico: leia o comando, identifique o primeiro erro,
reproduza a bancada individual e investigue o vetor ou a instrução apontada.
Após corrigir, refaça o teste local e a regressão. Não altere referências ou
`enabled.json` apenas para obter PASS.

## Exercício e critério para avançar

Um arquivo CSV continua com 47/47 depois de uma falha: isso prova que o código atual
passou? Não. Ele pode ser resultado da rodada anterior. Confira status, hashes,
logs e saída do comando. Avance com regressão PASS e sabendo distinguir evidência
de uma rodada de arquivos históricos que permanecem no disco.
