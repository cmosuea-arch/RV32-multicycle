# Fechamento funcional de 47 instruções — 27/10/2026

Marco Git: `isa-47-v1`. **47/47 (100%)** sob o
[contrato EEI CMOS](../../../docs/architecture/system.md), com 33 TBs PASS
(14 unitários + 19 integrações), lint dos dois tops e firmware oficial PASS.
Não houve síntese, fluxo físico ou signoff nesta rodada.

## Resultados

| Verificação | Resultado / evidência |
|---|---|
| Regressão completa | [33 TBs e hashes de 94 arquivos](logs/regression.json) |
| FENCE | 512 execuções integradas, máscaras/campos variados, store/FENCE/load; mais cinco aposentadorias no trace ISA |
| ECALL / EBREAK | 256 traps precisos de cada tipo, PC/motivo corretos, sem aposentadoria, RF/store posteriores bloqueados, reset recupera FETCH |
| Evidência de sistema | [Log do TB](logs/tb_core_system.log), [manifesto](logs/system.json), [decoder](logs/tb_decoder.log), [FSM](logs/tb_control_unit.log) |
| ISA sequencial | [88.794 aposentadorias, 46 stores e 12 bytes finais](logs/tb_isa.log); ECALL/EBREAK não entram como aposentadorias |
| Decoder | 131.138 palavras em dois perfis CRC; SYSTEM exatas e vizinhas de um bit |
| Firmware próprio | 598 aposentadorias, 2579 ciclos, assinatura 600dc0de |
| simple_system | Nove cenários RTL, incluindo encaminhamento de ambos os traps pela saída fault |
| Firmware oficial | [252 aposentadorias, 1026 ciclos, 16 CRCs e 44 tipos](logs/tb_official_firmware.log), x4=0 e três commits do loop |
| Waveform oficial | [VCD comprimido](official.vcd.gz), [log](logs/tb_official_firmware.wave.log), [conferência](waveform.json), [figura](official-success.png) |
| Automação | [Sete testes contra cobertura falsa](logs/coverage_gate.log), [cinco do conversor](logs/official_image_tests.log), [cinco de preflight](logs/openlane_preflight_tests.log); o preflight não executa síntese |

O firmware upstream fixado em edc7d599 não contém FENCE/ECALL/EBREAK. A coluna
Firmware oficial da matriz registra **NÃO EXERCITADA** para essas três, sem
atribuir a elas um PASS oficial. A imagem não foi modificada para aumentar
cobertura. Os testes próprios completam o perfil funcional no ambiente documentado.

ECALL/EBREAK são pedidos terminais ao ambiente, separados de instrução ilegal:
trap_o, trap_ebreak_o e trap_pc_o ficam disponíveis até reset. Não há serviços de
sistema, retorno de trap, CSRs ou arquitetura privilegiada. FENCE usa a ordenação
serial de memórias sem pedidos pendentes; mudar essa interface exige revalidá-la.
Um protocolo adicional exigido pela organização deve ser confrontado com o EEI.

## Reprodução

Na raiz, execute um comando por vez:

```bash
make official-fetch  # primeira obtenção da imagem fixada; depois os testes são offline
make system
make regression
make official-wave
python3 scripts/regression/test_coverage.py
python3 scripts/sim/test_build_official.py
```

Ferramentas em [tools.json](tools.json), captura em [capture.json](capture.json)
e inventário da imagem em [official_image.json](official_image.json). Os arquivos
originais upstream continuam no cache ignorado e podem ser recuperados por SHA.
Os hashes do manifesto identificam exatamente o RTL/TBs/scripts testados.

A [rodada anterior de CRC](../crc-official-20261027/README.md) preserva o teste
negativo contra a implementação antiga. Síntese genérica e evidências físicas
anteriores continuam históricas; não representam esta versão. Diagramas
ChipInventor, interface final, resultados físicos, vídeo e pacote ainda faltam.
