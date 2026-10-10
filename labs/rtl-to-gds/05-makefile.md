# 5 — Makefile: nomes curtos para receitas reproduzíveis

[Anterior](04-scripts-python.md) · [Índice](README.md) · [Próxima](06-regressao-e-evidencias.md)

## Objetivo e arquivo

Entender a construção do [Makefile real](../../Makefile) relacionando cada alvo
ao comando Python ou shell que você já conhece.

## Da linha manual à receita

Na aula anterior usamos:

```bash
python3 scripts/regression/run.py --suite unit
```

Para dar um nome a essa ação, o Makefile contém:

```make
# O alvo unit executa a receita abaixo.
unit:
	$(PYTHON) scripts/regression/run.py --suite unit
```

`unit` é o alvo; a linha recuada é sua receita. O recuo da receita deve ser um
**TAB real**, não espaços. Se estiver escrevendo um Makefile e encontrar
`missing separator`, confira esse caractere.

Make também pode trabalhar com dependências, usando a forma
`alvo: dependencias`. No arquivo atual, os alvos são ações sem grafo de dependências
por arquivo. `.PHONY` declara isso e evita que um arquivo chamado `unit` impeça a
receita. Cada chamada executa de novo; o Python controla a sequência interna.

`PYTHON` é uma variável: o Makefile escolhe `.venv/bin/python` quando instalado,
ou `python3` caso contrário. Também aceita `make unit PYTHON=/caminho/do/python`.
`make setup`, `make update` e `make doctor` preparam e conferem esse ambiente;
eles são explicados em [setup.md](../../docs/setup.md).

## Variáveis passadas no terminal

```make
# TB recebe, por exemplo, tb_alu pela linha de comando.
tb:
	$(PYTHON) scripts/regression/run.py --test $(TB)
```

```bash
make -n tb TB=tb_alu
make tb TB=tb_alu
```

`$(TB)` é expandido por Make antes de enviar a receita ao shell. `-n` mostra a
receita sem executá-la nestes alvos. Informe um nome simples, como `tb_alu`;
sem `TB`, o Python rejeita a ausência do argumento de `--test`.

## Mapa das ações existentes

| Comando | Processo | Evidência agregada |
|---|---|---|
| `make tb TB=tb_alu` | uma bancada | log da bancada |
| `make unit` | 13 TBs unitários | logs individuais |
| `make integration` | 15 TBs de integração, com firmware próprio | logs individuais |
| `make smoke` | quatro integrações rápidas | logs individuais |
| `make lint` | Verilator sem simulação | `lint.log` |
| `make test` | todos os TBs, sem lint | manifesto com lint `NOT_RUN` e cobertura |
| `make regression` | todos os TBs e lint | manifesto com lint `PASS` e cobertura |
| `make firmware` | GCC e conversão da imagem | log de build, ELF e hex |
| `make wave` | firmware no RTL com VCD | log e waveform |
| `make openlane-env-check` | script shell → Docker → verificador | resultado no terminal |
| `make openlane-env-smoke` | script shell → Docker → exemplo físico | resultado no terminal |
| `make openlane-shell` | sessão interativa no contêiner | shell com ferramentas físicas |

Sem argumento, `make` executa o primeiro alvo normal, `test`. Para fechamento use
explicitamente `make regression`, incluindo lint.

## Execução guiada

```bash
make -n unit
make -n integration
make -n regression
make -n openlane-env-smoke
```

Para cada linha impressa, encontre no Python ou shell o argumento correspondente.
No caso físico, o Make chama `environment.sh smoke`; esse shell é que inicia o
contêiner e chama LibreLane. O Make não faz síntese por conta própria.

Depois execute novamente uma receita pequena:

```bash
make tb TB=tb_rf_alu
```

O resultado deve ser o mesmo da execução direta feita na aula 3.

## Erros e execução sequencial

Uma ferramenta retorna um código de saída ao terminar. O executor Python transforma
falhas em saída diferente de zero; Make então interrompe a receita e informa erro.
Leia a mensagem anterior do Python e o log indicado para achar a causa original.

Use um comando por vez. `make -j` não é apropriado para estes alvos: eles escrevem
nos mesmos arquivos gerados e logs e não possuem isolamento para execução paralela.

## Exercício e critério para avançar

Qual a diferença entre `make firmware` e `make tb TB=tb_firmware`?
O primeiro só produz a imagem; o segundo também a executa no processador simulado
e verifica a assinatura. Avance quando conseguir seguir uma receita até a ferramenta
final e explicar por que Make e Python são camadas diferentes.
