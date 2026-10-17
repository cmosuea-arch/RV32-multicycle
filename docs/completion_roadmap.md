# Roteiro de conclusão e submissão

Atualizado em **2026-10-17**. Acompanhamento da ordem acordada com a equipe.
Baseline: **41/47 (87,23%)**. CRC experimental: três operações adicionais.
O fechamento oficial depende das definições registradas em
[official_questions.md](architecture/official_questions.md).

| Ordem | Entrega | Estado / próximo resultado verificável |
|---|---|---|
| 1 | Definições oficiais | Aguardando esclarecimentos CRC/sistema/top e firmware; usuário confirmou ausência de envio em 17/10 |
| 2 | CRC oficial, até 44/47 | Implementação provisória testada; falta confrontar contrato oficial e repetir verificações após ajustes |
| 3 | Sistema/sincronização, até 47/47 | Aguardando nomes, códigos e semântica oficiais |
| 4 | Top final | Integração atual funcional; fechar pinos/periféricos/capacidades e implementação das memórias |
| 5 | Firmware oficial | Aguardando arquivo/protocolo; executar até o final e guardar logs/waveforms |
| 6 | Congelamento RTL | Regressão final, evidências, cobertura e tag da versão de entrega |
| 7 | Desenhos | Datapath+controle atuais prontos no relatório; diagramas ChipInventor com outro colaborador |
| 8 | Fluxo físico | Configuração/restrições, mapeamento, layout, verificações, área/densidade e GDSII |
| 9 | Relatório final | v0.4 sucinta com 12 páginas; oito disponíveis para diagramas/resultados; completar autoria, figuras ChipInventor e resultados oficiais/físicos |
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
Isso conclui a figura do datapath **da implementação atual**, sem encerrar
a definição do RTL final ou das instruções pendentes.

Enquanto o item 1 aguarda a organização, podem avançar as figuras dos blocos
estáveis, evidências próprias e autoria/redação. As imagens reais de waveform
do firmware próprio já foram incorporadas à seção 6, com
[evidência reproduzível](../results/experiments/firmware-wave/README.md).
A revisão sucinta do relatório foi concluída; diagramas ChipInventor estão sob
responsabilidade de outro colaborador. Faltam receber as figuras, preencher
autoria e obter os materiais oficiais. A execução funcional/física será retomada
na etapa posterior combinada com o usuário. O waveform oficial exige receber
e executar aquele programa.

Critérios detalhados da entrega: [report/conformidade.md](report/conformidade.md).
Situação técnica e evidências: [status.md](status.md).

## Prática guiada no workspace atual

Por decisão do usuário em 17/10/2026, não será criada uma branch de entrega
separada para a atividade. Build/logs/ondas foram arquivados para recomeçar a
execução de forma acompanhada. O objetivo é compreender cada etapa e explicar
o sistema no vídeo. Siga a [prática para o vídeo](../labs/rtl-to-gds/00-pratica-para-video.md).
A preparação não executou testes; as próximas evidências serão geradas pelo usuário.
As pendências oficiais e físicas da entrega continuam registradas acima.
