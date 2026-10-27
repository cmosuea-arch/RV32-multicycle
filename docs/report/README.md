# Relatório da Fase 2 — versão de trabalho

- [Relatório editável](relatorio.md): redação técnica nos seis tópicos do guia.
- [Prévia PDF](relatorio-preliminar.pdf): versão preliminar, não pronta para submissão.
- [Conferência dos requisitos](conformidade.md): exigência, página de origem e pendência.

**Versão 0.6, 27/10:** CRC adequado, 44/47 instruções, 32 TBs/lint e firmware
oficial PASS. O PDF inclui a figura F21 real, conferida com log/VCD, mantendo
12 páginas e espaço para diagramas/resultados físicos.
[Evidências da rodada](../../results/experiments/crc-official-20261027/README.md).
A síntese da nova versão não foi executada, conforme orientação do usuário.

O documento descreve arquitetura, desenvolvimento incremental, RTL, testes,
automação, firmware e síntese lógica. As rodadas de referência permanecem
identificadas. Em 17/10 o firmware próprio foi reexecutado isoladamente para
produzir as figuras reais de waveform; os logs existentes foram preservados.
As capturas próprias de 17/10 são históricas. A nova rodada de 27/10 inclui
regressão e firmware oficial; implementação física continua pendente.

Revisão histórica **0.5, 20/10/2026**: mensagens da organização encaminhadas pelo usuário
identificam CCITT-FALSE para CRCB/CRCH/CRCW e testes assembly carregados na IMEM.
O algoritmo atual coincide quando a seed é `0xFFFF`; operandos/bytes ainda
carecem de confirmação. O firmware oficial ainda não foi recebido. A revisão
atualiza texto/PDF e preserva as evidências históricas, sem alterar RTL ou
executar nova regressão. [Registro completo](../architecture/clarifications_20261020.md).

## Fonte normativa consultada

Foi lido o [PDF local da competição](../../Champion-chip-guia-fase-2.pdf),
versão 1.0/2026, 24 páginas: Guia de Submissão nas páginas físicas 2–4 e Block
Guide nas páginas 6–23. O guia exige tópicos 1–6, PDF e no máximo 20 páginas.
A consulta para esta redação ocorreu em 15/10/2026. O hash do arquivo está na
[conferência](conformidade.md).

Este é o documento normativo disponível no repositório. Não há aqui um
regulamento geral separado nem comprovação de ausência de retificações na
plataforma. Antes de enviar, a equipe deve conferir eventuais instruções
adicionais da organização. Não se atribuem ao guia regras de fonte, margem ou
capa que ele não especifica.

## Atualizar e exportar

Edite `relatorio.md`. As marcações `<!-- pagebreak -->` organizam a paginação;
não aparecem como conteúdo no PDF. A exportação aceita os elementos usados no
rascunho: títulos, parágrafos, tabelas, código, links, negrito, itálico e imagens
PNG/JPEG locais em parágrafos próprios. A proporção das imagens é preservada.
Confira novamente paginação e legibilidade após incorporar novas figuras.

As dependências de edição ficam separadas do ambiente de simulação. Na raiz:

```bash
# Ambiente opcional, sem alterar o requirements.txt dos scripts RTL.
python3 -m venv build/report-venv
build/report-venv/bin/python -m pip install -r scripts/report/requirements.txt
build/report-venv/bin/python scripts/report/figures.py
build/report-venv/bin/python scripts/report/waveforms.py \
  --vcd results/experiments/firmware-wave/smoke.vcd.gz \
  --log results/experiments/firmware-wave/tb_firmware.wave.log
build/report-venv/bin/python scripts/report/build.py
```

Para reexportar a figura oficial a partir da captura identificada:

```bash
build/report-venv/bin/python scripts/report/official_waveforms.py \
  --vcd results/experiments/crc-official-20261027/official.vcd.gz \
  --log results/experiments/crc-official-20261027/logs/tb_official_firmware.wave.log \
  --output results/experiments/crc-official-20261027
```

A geração das figuras usa Ghostscript (`gs`); a fonte editável e a conferência
com o RTL estão em [architecture/figures](../architecture/figures/README.md).
O exportador usa fontes DejaVu em `/usr/share/fonts/truetype/dejavu` (pacote
Ubuntu `fonts-dejavu-core`). Se necessário, use `--font-dir /caminho/das/fontes`.
Também aceita `--source` e `--output`. Ele incorpora as fontes, conta páginas
com pypdf e só substitui o PDF de destino se o total for no máximo 20. Formatos
Markdown ainda não suportados causam erro explícito, evitando perda silenciosa
de conteúdo. Cabeçalho/rodapé identificam esta versão como preliminar.

O PDF é versionado e deve ser regenerado após editar o texto. A versão 0.4
reduziu o relatório de 19 para **12 páginas**, mantendo os seis tópicos exigidos,
44 codificações (41 baseline + 3 experimentais), os 17 módulos, o datapath e o
waveform de término. O corpo e as tabelas mantêm os tamanhos de fonte anteriores.
Comandos detalhados, aulas, inventários e evidências completas ficam referenciados
no repositório. As imagens próprias F20-A/B permanecem no repositório; o PDF v0.6 usa F21 oficial.

## Reserva editorial para a entrega

Os diagramas por módulo estão com outro colaborador. A reserva abaixo é um
planejamento; as oito páginas livres não foram adicionadas como páginas vazias.

| Conteúdo | Reserva de páginas adicionais |
|---|---|
| Diagramas ChipInventor dos 17 módulos, agrupados por função | Até 5 |
| Resultados físicos e imagem do GDSII | Até 1 |
| Complementos de evidência oficial, se necessários | Até 1 |
| Margem para revisão | 1 |

O relatório atual ocupa 12 páginas; esse planejamento chega ao limite de 20.
Inserir os diagramas próximos às tabelas das seções 4.1/4.2. Pinos e larguras
precisam permanecer legíveis: se um painel exigir mais espaço, redistribuir
texto/figuras. A quantidade acima não garante encaixe de imagens ainda não
recebidas. Evitar repetir a descrição do módulo na legenda.

Na revisão 0.6 houve correção do CRC, nova regressão e execução oficial no RTL.
A síntese e o fluxo físico continuam reservados ao usuário.

As figuras F20-A/B e seus logs/VCD/hashes estão em
[results/experiments/firmware-wave](../../results/experiments/firmware-wave/README.md).
Reexportar o arquivo arquivado mantém a origem da evidência. Para obter dados
do RTL atual, execute `make wave` e use `scripts/report/waveforms.py` sem opções;
essa execução atualiza build/logs conforme o fluxo de testes existente.

## Fechamento editorial

Preencher autoria/instituição; conferir instruções oficiais e a matriz ISA;
revisar o datapath após alterações do RTL; inserir figuras ChipInventor, layout
e waveforms;
substituir pendências por resultados comprovados; atualizar commit, fontes e
evidências; gerar o PDF final e revisar todas as páginas. O título e a marcação
de rascunho só devem mudar depois dessa revisão. A lista detalhada está em
[conformidade.md](conformidade.md).
