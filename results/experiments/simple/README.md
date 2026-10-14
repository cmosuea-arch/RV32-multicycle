# simple_system — validação em 2026-10-13

Escopo: sistema experimental, CRC CMOS provisório e síntese lógica genérica.
Não é submissão final nem fluxo físico OpenLane.

Executado em cópia isolada `/tmp/cmos-simple-*` para preservar logs locais:

```bash
make simple-system
make simple-synth
make regression
```

| Checagem | Resultado |
|---|---|
| Build do firmware | PASS; imagem 608/2048 bytes, BSS 32 bytes |
| Sistema RTL | PASS; 7 cenários de boot/reset/assinatura/fault |
| Regressão | PASS; 31 TBs (14 unitários + 17 integração) |
| Lint | PASS; riscv_top e simple_system elaborados separadamente |
| Síntese genérica Yosys | PASS; 32922 células genéricas |
| Memórias após síntese | Mapeadas; nenhum atributo init de registrador |
| Saídas | done/success/fault não constantes |
| Netlist simulada | PASS; dois boots com CRC e RAM inicialmente indefinida |

Yosys usado: 0.39+124 (d73f71e81). A contagem de células depende da versão e
não é área física; não há PDK, timing, DRC/LVS ou GDSII nesta execução.

Foi detectada e corrigida uma diferença RTL/síntese na IMEM: preencher zeros
antes de `$readmemh` produzia ROM zerada na netlist. As alternativas agora são
exclusivas; com arquivo, os geradores fornecem todas as palavras. O teste da
netlist verifica o programa completo após essa correção.

`regression.json`: hashes dos arquivos funcionais e resultado da regressão.
`simple_synth.json`: hashes de RTL, imagem ROM e netlist, ferramentas e células.
Logs selecionados copiados da execução isolada. A netlist/ROM são regeneráveis
em `build/`, não versionadas. Logs antigos do usuário em `results/logs/` foram
preservados e não devem ser confundidos com esta rodada.

Cobertura da baseline: **41/47 (87,23%)**. CRCB/CRCH/CRCW passam sob o contrato
CMOS provisório, incluindo firmware próprio; confirmação/firmware oficial pendentes.
