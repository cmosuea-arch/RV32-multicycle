# Roteiro de conclusão e submissão

Atualizado em **2026-10-27**. Acompanhamento da ordem acordada com a equipe.
Perfil atual: **47/47 (100%)**, CRC oficial e firmware publicado PASS em RTL.
O fechamento oficial depende das definições registradas em
[official_questions.md](architecture/official_questions.md).

| Ordem | Entrega | Estado / próximo resultado verificável |
|---|---|---|
| 1 | Definições oficiais | CRC e término identificados; RV32I identifica FENCE/ECALL/EBREAK; EEI CMOS implementado; top final pendente |
| 2 | CRC oficial, 44/47 | Concluído funcionalmente: unidade/core/ISA/firmware e regressão PASS |
| 3 | Sistema/sincronização, até 47/47 | Concluído funcionalmente sob o [EEI CMOS](architecture/system.md): FENCE e traps precisos; 33 TBs/lint PASS |
| 4 | Top final | Integração atual funcional; fechar pinos/periféricos/capacidades e implementação das memórias |
| 5 | Firmware oficial | PASS na revisão edc7d59: 252 aposentadorias/1026 ciclos, x4 e loop final; log/VCD/figura arquivados |
| 6 | Congelamento RTL | Regressão final, evidências, cobertura e tag da versão de entrega |
| 7 | Desenhos | Datapath+controle atuais prontos no relatório; diagramas ChipInventor com outro colaborador |
| 8 | Fluxo físico | Configuração experimental preparada para execução manual; faltam rodada concluída, revisão e resultados finais |
| 9 | Relatório final | v0.7 com 47/47 e execução oficial de 27/10; manter reserva de diagramas/resultados e completar autoria e resultados oficiais/físicos |
| 10 | Vídeo | Produzir 5–7 minutos, disponibilizar no YouTube e conferir os seis temas do guia |
| 11 | Submissão | Conferir regras atuais e reunir PDF, GDSII, GL, config.json, código/TBs e link do vídeo |

## Incremento concluído nesta revisão

- [x] Rever o guia local e as questões oficiais; registrar a resposta da equipe.
- [x] Desenhar execução, PC/memória e controle conforme o RTL atual.
- [x] Exportar SVG/PNG e incorporar os três painéis ao PDF.
- [x] Conferir a apresentação e o limite de 20 páginas.
- [x] Reexecutar o firmware próprio isoladamente e arquivar VCD/logs/hashes.
- [x] Incorporar waveforms reais de boot e escrita da assinatura ao relatório.
- [x] Enxugar o relatório e reservar espaço editorial para as imagens.
- [ ] Receber do colaborador os diagramas por módulo no ChipInventor e incorporá-los.

Os desenhos estão em [architecture/figures/](architecture/figures/README.md).
Isso conclui a figura do datapath **da implementação atual**. O perfil de 47 tipos
já passa sob o EEI CMOS; a interface e os diagramas finais ainda faltam.

Enquanto o item 1 aguarda a organização, podem avançar as figuras dos blocos
estáveis, evidências próprias e autoria/redação. As imagens reais de waveform
do firmware próprio já foram incorporadas à seção 6, com
[evidência reproduzível](../results/experiments/firmware-wave/README.md).
A revisão sucinta do relatório foi concluída; diagramas ChipInventor estão sob
responsabilidade de outro colaborador. Faltam receber as figuras, preencher
autoria e concluir os resultados físicos. O firmware oficial já foi recebido,
executado e capturado; a implementação física fica para execução pelo usuário.

Critérios detalhados da entrega: [report/conformidade.md](report/conformidade.md).
Situação técnica e evidências: [status.md](status.md).

## Esclarecimentos de 20/10

Registro histórico anterior à [fonte recebida em 27/10](architecture/crc_official_20261027.md).

O [registro recebido](architecture/clarifications_20261020.md) reduz P01: o
algoritmo é CCITT-FALSE, mas ainda não há vetores/pseudocódigo dos operandos.
O usuário confirmou não dispor desses detalhes. O firmware próprio já é
convertido em instruções da IMEM, como solicitado; não é necessário aguardar
o programa oficial para continuar verificando a implementação própria.
Isso não encerra a validação oficial nem altera a contagem de conformidade.

Por orientação do usuário em 20/10, a síntese será executada por ele. Foram
preparados o [formulário CRC](architecture/crc_official_confirmation.md), o
[recebimento do firmware](../firmware/official/receipt.md) e o
[roteiro de síntese física experimental](../openlane/simple_system/README.md).
Uma tentativa automatizada anterior não produziu resultado final; não há nova
síntese SKY130A aprovada nesta preparação.

## Revisão do firmware em 27/10

O CRC foi corrigido e a imagem publicada passou no core. A regressão desse incremento
aprova 32 TBs/lint, o teste negativo rejeita o CRC anterior e o VCD oficial foi
conferido com o log. Não houve síntese, conforme orientação do usuário. A imagem
contém 44 tipos. Em seguida, sistema/sincronização foi implementado e validado
sob o [EEI CMOS](architecture/system.md): 47/47 e 33 TBs/lint PASS. A interface
final permanece pendente. [Nova rodada](../results/experiments/isa-47-20261027/README.md).

## Prática guiada no workspace atual

Por decisão do usuário em 17/10/2026, não será criada uma branch de entrega
separada para a atividade. Build/logs/ondas foram arquivados para recomeçar a
execução de forma acompanhada. O objetivo é compreender cada etapa e explicar
o sistema no vídeo. Siga a [prática para o vídeo](../labs/rtl-to-gds/00-pratica-para-video.md).
A preparação inicial não executou testes; as rodadas posteriores estão arquivadas.
As execuções guiadas do usuário gerarão seus próprios logs e ondas.
As pendências oficiais e físicas da entrega continuam registradas acima.
