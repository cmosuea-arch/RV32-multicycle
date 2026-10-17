# Relatório da Fase 2 — versão de trabalho

- [Relatório editável](relatorio.md): redação técnica nos seis tópicos do guia.
- [Prévia PDF](relatorio-preliminar.pdf): versão preliminar, não pronta para submissão.
- [Conferência dos requisitos](conformidade.md): exigência, página de origem e pendência.

O documento descreve arquitetura, desenvolvimento incremental, RTL, testes,
automação, firmware e síntese lógica. As rodadas de referência permanecem
identificadas. Em 17/10 o firmware próprio foi reexecutado isoladamente para
produzir as figuras reais de waveform; os logs existentes foram preservados.
Não houve nova regressão completa nem implementação física.

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

A geração das figuras usa Ghostscript (`gs`); a fonte editável e a conferência
com o RTL estão em [architecture/figures](../architecture/figures/README.md).
O exportador usa fontes DejaVu em `/usr/share/fonts/truetype/dejavu` (pacote
Ubuntu `fonts-dejavu-core`). Se necessário, use `--font-dir /caminho/das/fontes`.
Também aceita `--source` e `--output`. Ele incorpora as fontes, conta páginas
com pypdf e só substitui o PDF de destino se o total for no máximo 20. Formatos
Markdown ainda não suportados causam erro explícito, evitando perda silenciosa
de conteúdo. Cabeçalho/rodapé identificam esta versão como preliminar.

O PDF é versionado para leitura direta e deve ser regenerado após editar o
texto. A versão 0.3 possui 19 páginas, incluindo os três painéis do datapath,
duas imagens reais de waveform e referências. Resta uma página de margem;
será necessário reorganizar/compactar conteúdo para os resultados finais.
Inserir os 17 diagramas de módulo
exigirá composição compacta e revisão editorial; a margem não garante que
todas as figuras futuras caibam sem reorganizar o texto.

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
