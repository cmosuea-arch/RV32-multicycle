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

| ID | Origem | Exigência | Local no relatório | Situação da versão 0.1 |
|---|---|---|---|---|
| R01 | §1, p. 2 | Objetivo, arquitetura, módulos, funcionamento e funcionalidades | §1 | Redigido para o escopo atual |
| R02 | §2, pp. 2–3 | Quantidades esperadas/implementadas e percentual por categoria | §2.1 | 41/47; CRC experimental identificado separadamente |
| R03 | §2, p. 3 | Lista de instruções por categoria | §2.2 | Incluída; sistema oficial pendente |
| R04 | §2, p. 3 | Tabela opcode/funct3/funct7 das instruções implementadas | §§2.4–2.6 | 41 da baseline + 3 experimentais; conferida com CSV |
| R05 | §3, p. 3 | Desenho completo do datapath com unidade de controle | §3 | Esquema textual provisório; incorporar figura completa e legível |
| R06 | §4, p. 3 | Explicação de cada módulo desenvolvido | §§4.1–4.3 | 17 módulos descritos, incluindo tops e experimento |
| R07 | §4, p. 3 | Diagrama por módulo feito no ChipInventor | §§4.1–4.3 | F02–F18 pendentes; Mermaid não é evidência de autoria no ChipInventor |
| R08 | §4, p. 3 | Testbenches individuais | §4 e código da entrega | 14 unitários e 17 integrações identificados; anexar todo o código no pacote |
| R09 | §5, p. 4 | Área total e densidade após fluxo OpenLane | §5.1 | Pendentes; células genéricas não preenchem área física |
| R10 | §5, p. 4 | Imagem do GDSII final | §5.1 | F19 pendente; GDS do exemplo da ferramenta não serve como resultado do processador |
| R11 | §6, p. 4 | Waveforms comprovando execução do firmware de validação | §6 | F21 oficial pendente; F20 próprio é evidência complementar |
| R12 | §6, p. 4 | Logs do TB mostrando conclusão sem erros | §6 | Log próprio incluído; log do firmware oficial pendente |
| R13 | §7, p. 4 | Vídeo de 5–7 min no YouTube cobrindo os seis temas indicados | Entregável separado | Pendente |
| R14 | §8, p. 4 | Relatório PDF contendo tópicos 1–6, máximo 20 páginas | PDF preliminar | Formato e tópicos presentes; 15 páginas; conteúdo final ainda incompleto |
| R15 | §9, p. 4 | Relatório, GDSII, GL, config.json e todo o código, incluindo TBs | Pacote de submissão | Código existente; PDF preliminar; resultados físicos ausentes |

O guia menciona a GL em `results/final/verilog/gl`. Verificar a localização
equivalente na versão do fluxo usada e separar o arquivo correto da execução
final. A netlist genérica de `make simple-synth` não é apresentada como a GL
final OpenLane exigida.

## Figuras e evidências a produzir

| Identificador | Conteúdo | Critério de revisão |
|---|---|---|
| F01 | Datapath completo + controle | Caminho de dados, muxes, registradores, enables, larguras, memória e CRC opcional |
| F02–F08 | ALU, RF, Immediate, PC, IR, IMEM, Branch Comparator | Exportação ChipInventor, pinos legíveis, correspondência ao RTL |
| F09–F13 | LSU, DMEM, Address Decoder, Decoder, FSM | Incluir controles, máscaras, latência e erros |
| F14–F18 | Multiplicador, CRC, Core, Top, simple_system | Identificar CRC e sistema experimental; alinhar top final |
| F19 | GDSII final do processador | Run, commit, top, escala e correspondência com área/densidade |
| F20 | Waveform do firmware próprio | Opcional complementar: boot e assinatura SW correta |
| F21 | Waveform do firmware oficial | Protocolo oficial, etapa final e ausência de erros, acompanhados de log |

As figuras podem ser agrupadas em painéis legíveis. A numeração é uma escolha
editorial, não uma exigência da organização. Este rascunho não contém imagens
simuladas ou ilustrativas apresentadas como waveforms reais.

## Controle dos resultados citados

| Afirmação | Evidência principal | Limite |
|---|---|---|
| 41/47 e codificações | `docs/isa/coverage.csv` | Contagem funcional da baseline; firmware oficial pendente |
| 31 TBs e lint PASS | `results/experiments/simple/regression.json` | Rodada de 13/10 local, 14/10 UTC; hashes identificam arquivos |
| CRC próprio PASS | `results/experiments/crc/` | Contrato CMOS; algoritmo oficial não confirmado |
| 598 aposentadorias, 2579 ciclos | `results/logs/tb_firmware.log` | Smoke próprio, não benchmark geral |
| 32922 células e dois boots na netlist | `results/experiments/simple/simple_synth.json`, `simple_netlist.log` | Yosys genérico, sem PDK/timing/área física |
| Ambiente físico aprovado | `results/openlane/environment-smoke.md` | Somente circuito de exemplo LibreLane |

Manifestos de rodadas anteriores não comprovam automaticamente o estado de
arquivos modificados depois. A redação usa evidências históricas identificadas;
o fechamento da entrega deve registrar uma rodada nova no commit final.

## Organização das páginas

Meta editorial atual: 15 páginas, com até cinco adicionais dentro do limite.
O limite considera conservadoramente tudo, inclusive identificação e referências,
pois o guia não informa exceções de contagem.

| Parte | Páginas do rascunho |
|---|---|
| Visão geral e método | 1–2 |
| Cobertura, lista e codificações | 3–5 |
| Datapath e sequenciamento | 6–7 |
| Módulos, testes e automação | 8–11 |
| Resultados físicos / síntese preparatória | 12 |
| Firmware e referências | 13–15 |

A4, fonte DejaVu, margens, referências e esta distribuição são escolhas de
edição. O guia consultado não determina template, ABNT, fonte ou margens.
Revisar paginação após incorporar imagens e resultados; não reduzir fontes
a ponto de comprometer a leitura para manter a contagem.

## Antes de submeter

- [ ] Conferir eventuais atualizações e regras adicionais da plataforma.
- [ ] Preencher integrantes, instituição e orientador e revisar autoria.
- [ ] Resolver P01–P04 em `docs/architecture/official_questions.md` e atualizar resultados.
- [ ] Conferir tabelas ISA com o RTL final, testes e firmware oficial.
- [ ] Incorporar datapath completo e diagramas ChipInventor de cada módulo.
- [ ] Preencher área/densidade e inserir imagem do GDSII do processador.
- [ ] Incluir waveform e logs do firmware oficial, declarando a etapa efetivamente atingida.
- [ ] Vincular relatório, RTL, testes, firmware e resultados físicos ao commit de entrega.
- [ ] Gerar PDF final, contar no máximo 20 páginas e revisar visualmente todas elas.
- [ ] Produzir vídeo de 5–7 minutos no YouTube: arquitetura, funcionamento, simulação, firmware, OpenLane e layout.
- [ ] Reunir relatório, GDSII, GL, config.json e todo o código/testbenches da mesma versão.

DRC/LVS, timing, hashes, regressão contínua e tag de fechamento são controles de
engenharia internos documentados em AGENTS.md. São úteis para a validade técnica,
mas não foram inventados como critérios de pontuação no Guia de Submissão.
