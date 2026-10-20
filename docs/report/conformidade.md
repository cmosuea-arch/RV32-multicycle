# Conferência do relatório e da submissão

Consulta: **15/10/2026**. Documento: [Champion-chip-guia-fase-2.pdf](../../Champion-chip-guia-fase-2.pdf),
versão 1.0/2026, 24 páginas. Referências abaixo usam páginas físicas do arquivo
combinado. SHA-256:

```text
3107f22f7153aca25ea8f472be4dff7474b5c6b9b5b1f0d490da190f5e85ab41
```

O Guia de Submissão foi lido integralmente (pp. 2–4), junto ao Block Guide que
o acompanha. Esta lista distingue exigências expressas do guia de escolhas
editoriais e critérios internos CMOS. Não certifica atendimento a regulamento
geral ou retificações que não estejam nesse arquivo.

## Requisitos expressos do guia

| ID | Origem | Exigência | Local no relatório | Situação da versão 0.4 |
|---|---|---|---|---|
| R01 | §1, p. 2 | Objetivo, arquitetura, módulos, funcionamento e funcionalidades | §1 | Redigido para o escopo atual |
| R02 | §2, pp. 2–3 | Quantidades esperadas/implementadas e percentual por categoria | §2.1 | 41/47; CRC experimental identificado separadamente |
| R03 | §2, p. 3 | Lista de instruções por categoria | §2.1 | Incluída junto à tabela de cobertura; sistema oficial pendente |
| R04 | §2, p. 3 | Tabela opcode/funct3/funct7 das instruções implementadas | §§2.3–2.5 | 41 da baseline + 3 experimentais; conferida com CSV |
| R05 | §3, p. 3 | Desenho completo do datapath com unidade de controle | §3 | Três painéis SVG/PNG incluídos, conferidos com o RTL atual; rever se houver alteração funcional |
| R06 | §4, p. 3 | Explicação de cada módulo desenvolvido | §§4.1–4.2 | 17 módulos descritos, incluindo tops e experimento |
| R07 | §4, p. 3 | Diagrama por módulo feito no ChipInventor | §§4.1–4.2 | F02–F18 pendentes, sob responsabilidade de outro colaborador |
| R08 | §4, p. 3 | Testbenches individuais | §4 e código da entrega | 14 unitários e 17 integrações identificados; anexar todo o código no pacote |
| R09 | §5, p. 4 | Área total e densidade após fluxo OpenLane | §5 | Pendentes; células genéricas não preenchem área física |
| R10 | §5, p. 4 | Imagem do GDSII final | §5 | F19 pendente; GDS do exemplo da ferramenta não serve como resultado do processador |
| R11 | §6, p. 4 | Waveforms comprovando execução do firmware de validação | §6 | F20-B no PDF; F20-A arquivado como apoio; F21 oficial pendente |
| R12 | §6, p. 4 | Logs do TB mostrando conclusão sem erros | §6 | Nova execução própria de 17/10 com log/VCD/hashes; log oficial pendente |
| R13 | §7, p. 4 | Vídeo de 5–7 min no YouTube cobrindo os seis temas indicados | Entregável separado | Pendente |
| R14 | §8, p. 4 | Relatório PDF contendo tópicos 1–6, máximo 20 páginas | PDF preliminar | Formato e tópicos presentes; 12 páginas; oito disponíveis para diagramas/resultados; conteúdo final incompleto |
| R15 | §9, p. 4 | Relatório, GDSII, GL, config.json e todo o código, incluindo TBs | Pacote de submissão | Código existente; PDF preliminar; resultados físicos ausentes |

O guia menciona a GL em `results/final/verilog/gl`. Verificar a localização
equivalente na versão do fluxo usada e separar o arquivo correto da execução
final. A netlist genérica de `make simple-synth` não é apresentada como a GL
final OpenLane exigida.

## Figuras e evidências a produzir

| Identificador | Conteúdo | Critério de revisão |
|---|---|---|
| F01-A/B/C | Datapath completo + controle | Incluídos nas páginas 5–7; fontes em architecture/figures/ |
| F02–F08 | ALU, RF, Immediate, PC, IR, IMEM, Branch Comparator | Exportação ChipInventor, pinos legíveis, correspondência ao RTL |
| F09–F13 | LSU, DMEM, Address Decoder, Decoder, FSM | Incluir controles, máscaras, latência e erros |
| F14–F18 | Multiplicador, CRC, Core, Top, simple_system | Identificar CRC e sistema experimental; alinhar top final |
| F19 | GDSII final do processador | Run, commit, top, escala e correspondência com área/densidade |
| F20-A/B | Waveform do firmware próprio | F20-B no PDF; boot F20-A como apoio. Ambos com VCD/logs/hashes arquivados |
| F21 | Waveform do firmware oficial | Protocolo oficial, etapa final e ausência de erros, acompanhados de log |

As figuras podem ser agrupadas em painéis legíveis. A numeração é uma escolha
editorial, não uma exigência da organização. Este rascunho não contém imagens
simuladas ou ilustrativas apresentadas como waveforms reais.

## Controle dos resultados citados

| Afirmação | Evidência principal | Limite |
|---|---|---|
| 41/47 e codificações | `docs/isa/coverage.csv` | Contagem funcional da baseline; firmware oficial pendente |
| 31 TBs e lint PASS | `results/experiments/simple/regression.json` | Rodada de 13/10 local, 14/10 UTC; hashes identificam arquivos |
| CRC próprio PASS | `results/experiments/crc/` | CCITT-FALSE identificado em 20/10; contrato de operandos/bytes ainda não confirmado |
| 598 aposentadorias, 2579 ciclos e SW em 25795 ns | `results/experiments/firmware-wave/` | Smoke próprio reexecutado; VCD e TB conferem a escrita; não é benchmark geral |
| 32922 células e dois boots na netlist | `results/experiments/simple/simple_synth.json`, `simple_netlist.log` | Yosys genérico, sem PDK/timing/área física |
| Ambiente físico aprovado | `results/openlane/environment-smoke.md` | Somente circuito de exemplo LibreLane |

Manifestos de rodadas anteriores não comprovam automaticamente o estado de
arquivos modificados depois. A redação usa evidências históricas identificadas;
o fechamento da entrega deve registrar uma rodada nova no commit final.

## Organização das páginas

Versão 0.5: **12 páginas**, liberando oito dentro do limite. A revisão 0.4 removeu
repetições e detalhes didáticos do PDF; descrições de módulos e testes foram
concentradas em tabelas. Os tamanhos de fonte foram preservados.

| Parte | Páginas do rascunho |
|---|---|
| Visão geral, arquitetura e método | 1 |
| Cobertura, lista e codificações | 2–4 |
| Datapath e controle | 5–7 |
| Módulos e testbenches | 8–9 |
| Resultados físicos e firmware | 10 |
| Waveform próprio de término | 11 |
| Referências | 12 |

Planejamento das oito páginas adicionais: até cinco para diagramas ChipInventor,
uma para resultados físicos/GDSII, uma para firmware oficial e uma de margem.
As figuras devem ser legíveis, com grupos por função próximos à descrição dos
módulos. O responsável pelos diagramas é outro colaborador, conforme informado
pelo usuário. Rever a paginação depois de receber as imagens reais.
O limite considera tudo, inclusive identificação e referências.

A4, fonte DejaVu, margens, referências e esta distribuição são escolhas de
edição. O guia consultado não determina template, ABNT, fonte ou margens.
Revisar paginação após incorporar imagens e resultados; não reduzir fontes
a ponto de comprometer a leitura para manter a contagem.

## Antes de submeter

- [ ] Conferir eventuais atualizações e regras adicionais da plataforma.
- [ ] Preencher integrantes, instituição e orientador e revisar autoria.
- [ ] Resolver P01–P04 em `docs/architecture/official_questions.md` e atualizar resultados.
- [ ] Conferir tabelas ISA com o RTL final, testes e firmware oficial.
- [x] Incorporar datapath/controle da versão atual (três painéis, revisados em 17/10/2026).
- [ ] Rever as figuras após mudanças de RTL e incorporar diagramas ChipInventor de cada módulo.
- [ ] Preencher área/densidade e inserir imagem do GDSII do processador.
- [x] Incluir waveform de término/log do firmware próprio e arquivar boot, VCD e hashes (17/10/2026).
- [ ] Incluir waveform e logs do firmware oficial, declarando a etapa efetivamente atingida.
- [ ] Vincular relatório, RTL, testes, firmware e resultados físicos ao commit de entrega.
- [ ] Gerar PDF final, contar no máximo 20 páginas e revisar visualmente todas elas.
- [ ] Produzir vídeo de 5–7 minutos no YouTube: arquitetura, funcionamento, simulação, firmware, OpenLane e layout.
- [ ] Reunir relatório, GDSII, GL, config.json e todo o código/testbenches da mesma versão.

DRC/LVS, timing, hashes, regressão contínua e tag de fechamento são controles de
engenharia internos documentados em AGENTS.md. São úteis para a validade técnica,
mas não foram inventados como critérios de pontuação no Guia de Submissão.

Revisão editorial de 17/10/2026: figuras F01-A/B/C incorporadas e PDF conferido
com 17 páginas. O usuário informou que a organização ainda não enviou as
definições nem o firmware oficial; essa dependência permanece aberta.

Revisão da captura em 17/10/2026: `make wave` executado em cópia isolada;
figuras F20-A/B incorporadas; PDF com 19 páginas. Apenas o TB do firmware próprio
foi reexecutado, sem nova regressão completa ou implementação física.

Revisão editorial 0.4: texto reduzido e tabelas consolidadas, PDF de 19 para
12 páginas; janela de boot preservada no repositório. Nenhum teste ou fluxo
físico foi reexecutado. Diagramas ChipInventor a cargo do colaborador responsável.

Revisão editorial 0.5, 20/10/2026: incorporadas as mensagens encaminhadas pelo
usuário. A variante CRC e a forma geral do firmware estão identificadas; faltam
contrato dos operandos/bytes e arquivo/protocolo oficial. Registro rastreável em
[clarifications_20261020.md](../architecture/clarifications_20261020.md).
Sem alteração RTL, nova regressão ou fluxo físico nesta revisão.
