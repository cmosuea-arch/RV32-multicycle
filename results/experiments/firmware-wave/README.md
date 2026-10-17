# Firmware próprio — waveform de 17/10/2026

Execução **PASS** de `make wave` em cópia isolada, a partir do RTL do commit
`7ddc6bf`. A simulação executou somente `tb_firmware`: **598 aposentadorias,
2.579 ciclos**, assinatura `0x600dc0de` em `0x10011ff0`, sem fault após reset.
O testbench verificou a palavra efetivamente armazenada na DMEM.

## Figuras

| Figura | Janela de simulação | Arquivos |
|---|---|---|
| F20-A — boot | 0–150 ns | [PNG](firmware-boot.png), [SVG](firmware-boot.svg) |
| F20-B — assinatura | 25.710–25.796 ns | [PNG](firmware-signature.png), [SVG](firmware-signature.svg) |

São traçados programáticos das mudanças do VCD, sem interpolação de valores ou
construção de estímulos esperados. Reset, clock, FSM, PC, instrução, commit,
oe/we, endereço, dado de store, byte write e fault vêm da captura real.
Redes X/Z são preservadas; os valores indefinidos antes da primeira borda de
reset são esperados nessa simulação. Buses aparecem em hexadecimal. Um segmento
curto demais para seu texto mantém a transição e omite o rótulo.

A escrita final ocorre na borda de **25.795 ns**, com estado MEMORY, `we=1`,
`bw=0xf`, endereço `0x10011ff0` e dado `0x600dc0de`. O TB encerra em 25.796 ns.
A transação é amostrada **antes da borda**; o VCD também contém as atualizações
NBA posteriores no mesmo timestamp. Contar apenas os patamares pós-borda daria
uma interpretação errada do store/commit. A instrução SW final ainda não foi
aposentada quando o TB termina; as 598 aposentadorias são as anteriores.

## Evidências e rastreabilidade

- [Log completo do TB](tb_firmware.wave.log): assinatura, contadores e término.
- [Log da compilação](tb_firmware.compile.log): RTL e bancada usados, sem diagnósticos.
- [Build do firmware](firmware_build.log) e [disassembly](smoke.disasm).
- [Saída do comando make](make-wave.log).
- [VCD completo comprimido](smoke.vcd.gz): fonte das imagens, preservada no Git.
- [capture.json](capture.json): commit de referência, diretório isolado, versões,
  hashes do snapshot, ROM e artefatos de execução.
- [waveform.json](waveform.json): escala, janelas, borda de assinatura, conferência
  de contadores e hashes do VCD, log e exportador.

O inventário do snapshot inclui os arquivos copiados, inclusive bancadas que
não foram executadas nesta rodada. Não é um manifesto de regressão completa.
O Makefile local tinha mudanças de espaçamento, preservadas no snapshot e
identificadas por hash. O RTL não tinha alterações locais. Logs correntes do
workspace foram preservados; caminhos `/tmp/cmos-firmware-wave-*` nos logs
identificam a cópia usada na execução, dispensável para ler as evidências.

## Reproduzir

Para uma **nova execução**, na raiz do projeto:

```bash
make wave
build/report-venv/bin/python scripts/report/waveforms.py
```

`make wave` usa os diretórios correntes de build/logs. Use uma cópia isolada se
quiser preservar a rodada anterior. O exportador confere os resultados antes
de desenhar as figuras; seus padrões de entrada são o VCD e log gerados pelo
comando acima.

Para **reexportar esta evidência arquivada**, sem executar o processador:

```bash
build/report-venv/bin/python scripts/report/waveforms.py \
  --vcd results/experiments/firmware-wave/smoke.vcd.gz \
  --log results/experiments/firmware-wave/tb_firmware.wave.log
build/report-venv/bin/python scripts/report/build.py
```

Ambiente opcional: [instruções do relatório](../../../docs/report/README.md).
O exportador usa ReportLab/fontes DejaVu e Ghostscript. A biblioteca padrão
Python lê o subconjunto digital do VCD emitido pelo Icarus; não é um visualizador
genérico de todos os formatos de waveform. Verificações dirigidas incluíram
leitura do arquivo bruto/comprimido e rejeição de assinatura, máscara,
contagem e fault adulterados.

## Limites

Firmware próprio da baseline, CRC desabilitado. Não é firmware oficial,
simulação de netlist ou pós-layout. O clock de 10 ns é um estímulo do testbench,
não comprovação de frequência máxima física. Esta rodada não repetiu os 31 TBs
nem lint. A cobertura permanece **41/47 (87,23%)**.
