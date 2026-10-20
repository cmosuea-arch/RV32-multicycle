# Estado do projeto — 2026-10-20

Versão parcial de entrega: `rtl-subset-v0.1`. **41/47 instruções (87,23%)**.
Matriz por instrução e categoria: [isa/coverage.md](isa/coverage.md).
Fonte RTL validada: tag `isa-41-v1` (`ea6bccd`); a tag da entrega também inclui
firmware, automação, documentação e evidências finais.

As tags acima identificam a baseline histórica. A versão atual acrescenta CRC
provisório (opt-in) e `simple_system`, conforme evidências em
[`results/experiments/`](../results/experiments/simple/README.md).

**Atualização da organização, recebida em 20/10:** CRCB/CRCH/CRCW usam
CRC-16-CCITT-FALSE, com 8/16/32 bits de dados e resultado de 16 bits. O algoritmo
coincide com o atual usando seed `0xFFFF`; falta confirmar o contrato dos
operandos e a ordem dos bytes. O firmware será um teste assembly para a IMEM,
com publicação prevista após autorização, ainda sem arquivo recebido. O usuário
informou não ter pseudocódigo/vetores adicionais. Veja o
[registro e comparação](architecture/clarifications_20261020.md).

| Marco | Estado | Evidência / limite |
|---|---|---|
| M0 — baseline | Parcial | Contratos dos blocos confirmados congelados; CRC/pinagem pendentes |
| M1 — datapath básico | PASS | PC + IMEM + IR e demais blocos básicos integrados |
| M2 — primeira instrução | PASS | ADD/SUB/ADDI, tag core-smoke-v1 |
| M3 — operações básicas | PASS | 21/47, tag isa-21-v1 |
| M4 — controle de fluxo | PASS | 29/47, tag isa-29-v1 |
| M5 — memória | PASS | 37/47, tag isa-37-v1 |
| M6 — Zmmul | PASS | 41/47, tag isa-41-v1 |
| M7/M8 — Xicrc e ISA completa | NOT DONE | Algoritmo CRC identificado; faltam contrato dos operandos e 3 instruções de sistema |
| Firmware próprio | PASS | C/assembly, assinatura 600dc0de; 598 aposentadorias, 2579 ciclos |
| M9 — firmware oficial | NOT DONE | Arquivo/protocolo de validação oficial ausentes |
| M10 — RTL final | NOT DONE | Faltam M7–M9 e interface final |
| M11/M12 — OpenLane/GDSII | Não iniciados | Pré-requisitos AGENTS.md §33 não atendidos |
| Ambiente físico | PASS | LibreLane/OpenROAD/SKY130A e smoke test 80/80 até GDSII |
| CRC experimental | PASS no contrato CMOS | 3 instruções; M7 oficial continua pendente |
| simple_system | PASS em RTL e netlist genérica | ROM 2 KiB/RAM 1 KiB, firmware próprio com CRC; sem fluxo físico |

Blocos ALU, Register File, Immediate, PC, IR, IMEM, Branch Comparator, LSU, DMEM,
Address Decoder e Multiplicador têm RTL, TB unitário, integração, diagrama Mermaid,
documentação, evidências PASS e commits identificados. Decoder, FSM e core estão
funcionais para as 41 instruções. Top de integração executável, top físico pendente.

Rodada funcional registrada em 2026-10-13: **31 testbenches PASS + lint Verilator PASS**, sem diagnósticos
de compilação Icarus. Teste ISA: **76.409 aposentadorias**, 45 stores físicos e
12 bytes finais comparados ao modelo Python. Decoder: 131.072 combinações de
opcode/funct3/funct7. Detalhes em [verification.md](verification.md).

O perfil experimental acrescenta CRCB/CRCH/CRCW às 41 instruções, mas não muda
a cobertura de conformidade: **41/47 (87,23%)**. A variante CRC escolhida inicialmente
coincide com CCITT-FALSE, identificada na mensagem de 20/10; o contrato de
operandos/bytes ainda exige confirmação antes de homologar as instruções.
O sistema mínimo passou também por síntese lógica e dois boots na netlist.

Para reproduzir: `make run` executa o firmware baseline, `make simple-system`
verifica o sistema experimental e `make simple-synth` gera/testa sua netlist.
O [laboratório](../labs/rtl-to-gds/README.md) possui oito aulas, com
[síntese na aula 7](../labs/rtl-to-gds/07-sintese.md) e preparação física na aula 8.
Consulte [synthesis.md](synthesis.md) para saídas e limites.

Pendências para retomar: [architecture/official_questions.md](architecture/official_questions.md).
O [relatório da Fase 2](report/README.md) possui versão preliminar v0.5 em Markdown/PDF,
com 12 páginas (antes 19), figuras do datapath/controle e waveform próprio de
término. O boot e demais logs/VCD/hashes continuam arquivados; há oito páginas
disponíveis para diagramas e resultados finais.
Os requisitos foram conferidos no guia. Os diagramas ChipInventor estão com
outro colaborador; as figuras,
resultados físicos, evidência do firmware oficial e vídeo ainda faltam para
fechar a submissão. Em 17/10 apenas o firmware próprio foi reexecutado para captura;
a regressão completa continua referida à rodada histórica identificada acima.
**O projeto completo e a parte RTL da competição permanecem NOT DONE.**

Ordem de execução e progresso: [roteiro de conclusão](completion_roadmap.md).
Em 17/10 o usuário confirmou que os esclarecimentos e o firmware ainda não
foram enviados pela organização. Esse é o registro histórico anterior às
mensagens de 19–20/10. As pendências restantes estão discriminadas acima;
a revisão atual concluiu as figuras do datapath e as evidências visuais próprias,
sem alterar RTL. Registro: [firmware-wave](../results/experiments/firmware-wave/README.md).

Revisão editorial v0.4 (histórico): descrições/testes consolidados em tabelas, sem reduzir
fontes ou executar novos testes. A execução do projeto fica para a etapa
posterior acordada com o usuário.

Preparação da prática em 17/10/2026: mesmo workspace/branch, build/logs/ondas
arquivados, sem nova simulação. [Histórico dos logs](../results/history/pre-guided-20261017/README.md)
e [percurso para o vídeo](../labs/rtl-to-gds/00-pratica-para-video.md).
As evidências do relatório permanecem intactas; a matriz publicada aponta aos
logs preservados até a próxima regressão completa.

Revisão de 20/10: comparação do CRC e da carga de firmware com as mensagens
recebidas; documentação/relatório atualizados. Modelo Python conferido para
CCITT-FALSE com agrupamentos de 1/2/4 bytes. Sem alteração RTL, nova regressão
ou execução física nesta revisão; as evidências PASS continuam nas rodadas
identificadas, sem antecipar M7, M9 ou 47/47.

Preparação posterior de 20/10, com síntese reservada ao usuário: contrato CRC
e [formulário do retorno oficial](architecture/crc_official_confirmation.md)
organizados, [recebimento do firmware](../firmware/official/receipt.md) preparado
e [configuração física experimental](../openlane/simple_system/README.md) disponível.
Os scripts de execução tiveram verificações estáticas e testes de barreiras de
entrada; a tentativa inicial de síntese SKY130A ficou sem resultado final e não
é PASS. Nenhuma nova rodada será iniciada automaticamente nesta preparação.
