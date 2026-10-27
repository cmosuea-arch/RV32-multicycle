# Estado do projeto — 2026-10-27

**47/47 instruções (100%)**, com Xicrc habilitado por padrão. Matriz:
[coverage.md](isa/coverage.md) / [Excel](isa/coverage.xlsx).
[Rodada identificada de 27/10](../results/experiments/isa-47-20261027/README.md).
O projeto completo permanece NOT DONE: interface final, diagramas, resultados
físicos e fechamento da entrega ainda faltam. Sistema/sincronização passa sob o
[contrato EEI CMOS](architecture/system.md), sem arquitetura privilegiada.

## Resultado atual

O firmware oficial, revisão edc7d5990d2185942081ee8a6899aa603cc91569, definiu
rs1=dados, rs2=CRC anterior e bytes mais significativos primeiro. RTL, modelo,
vetores e firmware próprio foram corrigidos. O parâmetro histórico
EXPERIMENTAL_XICRC agora vale 1 por padrão; 0 preserva o subconjunto sem CRC.
[Contrato implementado](architecture/crc.md).

| Marco | Estado | Evidência / limite |
|---|---|---|
| M0 — contratos | Parcial | Blocos implementados; interface final pendente |
| M1/M2 — datapath e primeira instrução | PASS | Regressão preserva os blocos e o primeiro programa |
| M3–M6 — RV32I/Zmmul | PASS | Tags históricas isa-21-v1 até isa-41-v1; nova regressão preservada |
| M7 — Xicrc | PASS funcional | Unidade, decoder, core, ISA e firmware oficial na revisão de 27/10 |
| M8 — ISA completa | PASS funcional no EEI CMOS | FENCE ordenada e traps precisos ECALL/EBREAK; 47/47 sob o contrato documentado |
| M9 — firmware oficial publicado | PASS na simulação RTL | 252 aposentadorias, 1026 ciclos, 16 CRCs, 44 tipos exercitados |
| M10 — RTL final | NOT DONE | Interface final, diagramas e tag final da entrega pendentes |
| M11/M12 — fluxo físico/GDSII | NOT DONE | Síntese da versão atual reservada ao usuário |
| Ambiente físico | PASS histórico | Smoke LibreLane do circuito de exemplo, sem validar o processador |
| simple_system | PASS em RTL | 9 cenários, firmware próprio ajustado; netlist anterior é histórica |

Regressão atual: **33 TBs PASS (14 unitários + 19 integrações) e lint dos dois tops PASS**.
ISA: 88.794 aposentadorias, 46 stores físicos e 12 bytes finais comparados.
CRC: 18.304 vetores e 2.146 operações em 32.930 aposentadorias no teste dedicado.
O decoder verifica 131.138 palavras (varredura de campos, SYSTEM exatas e vizinhas) com CRC habilitado e desabilitado.
Firmware próprio baseline: 598 aposentadorias/2579 ciclos e assinatura 600dc0de.

O programa oficial foi carregado a partir de firmware.txt, sem remontagem,
preservando 259 palavras e constantes da IMEM. A bancada exige a escrita de
x4=0 no término e três aposentadorias do loop final: o zero do reset não aprova.
O CRC anterior foi usado em teste negativo e terminou em x4=FFFFFFFF como esperado.
VCD, figura real e logs estão na rodada identificada; a escrita final ocorreu
em 10145 ns. Esse tempo é de simulação, sem caracterizar timing físico.

## Reproduzir e continuar

No WSL, um comando por vez:

```bash
make official-fetch   # obtém e verifica a revisão fixada; necessário uma vez por clone
make regression       # simulação e lint, sem síntese
make official-run     # somente o teste oficial
make official-wave    # nova captura do firmware oficial
```

O cache original é ignorado pelo Git e sobrevive a make clean. A adequação CRC
usou inicialmente uma cópia isolada; o fechamento `isa-47-v1` possui rodada
própria arquivada, com os hashes dos arquivos realmente executados.
As evidências e tags anteriores continuam históricas e não substituem essa rodada.

A síntese genérica antiga (32922 células/dois boots) é da versão anterior do CRC.
Não foi repetida, conforme orientação do usuário. Para a nova versão, o usuário
poderá executar make simple-synth e depois as etapas de exploração preparadas em
[openlane/simple_system](../openlane/simple_system/README.md). O experimento não
fecha automaticamente os requisitos físicos da competição.

## Pendências da entrega

1. Conferir eventual protocolo adicional de traps exigido pela competição; o
   [EEI CMOS](architecture/system.md) está implementado e testado. O firmware
   publicado cobre 44 tipos; as três de sistema têm testes próprios.
2. Fechar interface do top final, pinos/periféricos e estratégia física das memórias.
3. Incorporar os diagramas ChipInventor, a cargo do outro colaborador.
4. Executar/revisar síntese e fluxo físico da versão escolhida; obter área/densidade,
   timing, DRC/LVS/antena e GDSII identificados.
5. Fechar relatório, autoria, vídeo de 5–7 minutos, pacote e tag final.

O relatório preliminar v0.7 incorpora 47/47, contrato EEI e execução oficial, preservando espaço
para diagramas e resultados físicos. Fontes e lacunas:
[questões oficiais](architecture/official_questions.md) e
[roteiro de conclusão](completion_roadmap.md).

## Revisão dos comentários e material de estudo

O [guia de leitura](code_guide.md) conecta os arquivos, a sequência de execução
e os protocolos dos três programas. Referências antigas nas aulas/contrato CRC
foram corrigidas; registros históricos continuam identificados por data/tag.
A [conferência editorial](../results/experiments/documentation-20261027/README.md)
preservou a lógica de 35 arquivos e confirmou novamente 33 TBs/lint e firmware
oficial PASS em cópia isolada, sem síntese ou alteração dos logs da prática.
Os hashes dessa revisão ficam separados dos originais de `isa-47-v1`.
