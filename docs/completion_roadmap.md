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
| 7 | Desenhos | Datapath+controle atuais prontos no relatório; diagramas por módulo no ChipInventor pendentes |
| 8 | Fluxo físico | Configuração/restrições, mapeamento, layout, verificações, área/densidade e GDSII |
| 9 | Relatório final | v0.3 preliminar com 19 páginas, incluindo waveform próprio; completar autoria, figuras ChipInventor e resultados oficiais/físicos |
| 10 | Vídeo | Produzir 5–7 minutos, disponibilizar no YouTube e conferir os seis temas do guia |
| 11 | Submissão | Conferir regras atuais e reunir PDF, GDSII, GL, config.json, código/TBs e link do vídeo |

## Incremento concluído nesta revisão

- [x] Rever o guia local e as questões oficiais; registrar a resposta da equipe.
- [x] Desenhar execução, PC/memória e controle conforme o RTL atual.
- [x] Exportar SVG/PNG e incorporar os três painéis ao PDF.
- [x] Conferir a apresentação e o limite de 20 páginas.
- [x] Reexecutar o firmware próprio isoladamente e arquivar VCD/logs/hashes.
- [x] Incorporar waveforms reais de boot e escrita da assinatura ao relatório.
- [ ] Produzir os diagramas por módulo no ChipInventor.

Os desenhos estão em [architecture/figures/](architecture/figures/README.md).
Isso conclui a figura do datapath **da implementação atual**, sem encerrar
a definição do RTL final ou das instruções pendentes.

Enquanto o item 1 aguarda a organização, podem avançar as figuras dos blocos
estáveis, evidências próprias e autoria/redação. As imagens reais de waveform
do firmware próprio já foram incorporadas à seção 6, com
[evidência reproduzível](../results/experiments/firmware-wave/README.md).
Os próximos itens independentes são os diagramas ChipInventor dos blocos estáveis
e a revisão editorial/autoria. O waveform oficial só poderá ser produzido após
receber e executar aquele programa.

Critérios detalhados da entrega: [report/conformidade.md](report/conformidade.md).
Situação técnica e evidências: [status.md](status.md).
