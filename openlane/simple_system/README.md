# Configuração física experimental do simple_system

**Preparada para execução manual; ainda sem rodada SKY130A concluída.** O usuário
solicitou em 20/10/2026 executar pessoalmente a síntese. Uma tentativa inicial em
cópia temporária chegou à etapa de síntese, mas ficou sem resultado final e não
constitui evidência PASS. Nenhuma nova síntese é iniciada por esta preparação.

O circuito usa o contrato CRC atual, firmware próprio, ROM 2 KiB e RAM 1 KiB.
O fechamento do CRC é acompanhado em
[crc_official_confirmation.md](../../docs/architecture/crc_official_confirmation.md).
Esta configuração não fecha os marcos de submissão dependentes do firmware,
ISA e interface oficiais.

## Arquivos e escolhas iniciais

| Arquivo / parâmetro | Função / valor |
|---|---|
| [config.json](config.json) | Top simple_system e lista explícita de 16 arquivos RTL |
| [constraints.sdc](constraints.sdc) | SDC do fluxo mais atrasos mínimos das entradas/saídas |
| PDK / biblioteca | sky130A / biblioteca padrão da imagem, sky130_fd_sc_hd |
| Clock | clk_i, período de exploração 100 ns (10 MHz) |
| Ocupação inicial do núcleo | 35%; dimensões calculadas pelo fluxo |
| Densidade alvo de placement | 45% |
| Atraso máximo de I/O | 20% do período, aplicado pelo SDC padrão |
| Atraso mínimo de I/O | 0,5 ns |
| Incerteza / transição de clock | 0,5 / 0,2 ns |
| Carga das saídas | 20 fF, convertidos pelo SDC padrão |

São parâmetros de exploração, sujeitos à leitura dos relatórios. Reset síncrono
continua temporizado. A organização multiciclo da FSM não é uma justificativa
para relaxar todos os caminhos de STA com exceções multicycle.
O aviso TIMESCALEMOD é silenciado somente nos modelos blackbox do PDK, que não
trazem timescale; não há supressão de latch ou largura do nosso RTL.

## Executar quando decidir iniciar

Use o **terminal WSL**, na raiz do repositório. O wrapper abre o Docker sozinho.
Para estudar as receitas sem executar ferramentas:

```bash
make -n simple-openlane-synth
make -n simple-openlane-floorplan
make -n simple-openlane
```

Para executar de fato, escolha uma etapa por vez:

```bash
make simple-openlane-synth       # síntese mapeada e checkers da netlist
make simple-openlane-floorplan   # nova rodada até floorplan, incluindo STA inicial
make simple-openlane             # nova rodada completa; requer ler verificações finais
```

Cada alvo executa primeiro `make simple-synth`, recompilando o firmware e testando
dois boots da netlist genérica. O executor físico verifica esses hashes e copia
RTL, ROM, configuração e SDC para um diretório próprio de entradas. A ROM recebe
um caminho absoluto dentro da montagem, para não depender do diretório do Yosys.
Cada comando inicia uma rodada independente, sem sobrescrever rodadas anteriores.

## Onde ler o resultado

| Caminho | Conteúdo |
|---|---|
| results/logs/simple_openlane.json | Estado da tentativa mais recente e diretório da rodada |
| build/openlane-simple/data-UTC/console.log | Log completo do wrapper/LibreLane |
| build/openlane-simple/data-UTC/summary.json | Etapa solicitada, fontes, hashes e estado |
| build/openlane-simple/data-UTC/design/runs/run/ | Configuração resolvida, logs, estados e saídas do fluxo |

`PASS` se refere à etapa solicitada; `signoff_complete` permanece falso até
revisão técnica dos relatórios. A etapa synth não gera layout, e floorplan não
inclui placement/routing. A área de células da síntese não é a área final do die.
Antes de registrar resultados físicos, conferir etapa realmente alcançada,
warnings, células/sequenciais presentes, timing, DRC/LVS/antena e GDSII quando
aplicáveis. Uma mudança posterior do CRC/firmware exige nova rodada identificada.

Os testes do executor são independentes de síntese/Docker:

```bash
python3 scripts/openlane/test_run_simple.py
```

Referências primárias consultadas em 20/10: [configuração LibreLane](https://librelane.readthedocs.io/en/latest/reference/configuration.html),
[variáveis de etapas](https://librelane.readthedocs.io/en/latest/reference/step_config_vars.html)
e código/CLI da versão instalada 3.0.0rc1. Os arquivos estão preparados;
compatibilidade completa e resultados físicos dependem da sua execução.
