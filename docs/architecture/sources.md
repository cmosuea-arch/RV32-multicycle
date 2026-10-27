# Fontes verificadas

## Firmware oficial consultado em 27/10/2026

- [Repositório fornecido pelo usuário](https://github.com/championchip-experience-community/CCX_Brasil_Edition_Firmware_Stage_2),
  revisão `edc7d5990d2185942081ee8a6899aa603cc91569`.
- `firmware.s` define os usos de CRCB/CRCH/CRCW; `firmware.txt` fornece palavras
  e endereços; README descreve integração, x4 de término e mock físico.
- [Manifesto de origem](../../firmware/official/source.json), com hashes e URLs fixas.
  [Contrato extraído e diferenças do RTL](crc_official_20261027.md).
- Consulta de fontes e comparação Python; sem execução do core ou síntese.

## Baseline normativa

- `Champion-chip-guia-fase-2.pdf`, 24 páginas, versão 1.0/2026. Guia de Submissão
  nas páginas físicas 2–4; Block Guide nas páginas 6–23. Todas as referências
  locais usam páginas físicas do PDF combinado.
- [RV32I v2.1, publicação 20260120](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html).
- [M/Zmmul, publicação 20260120](https://docs.riscv.org/reference/isa/v20260120/unpriv/m-st-ext.html).
- Codificações oficiais: [riscv-opcodes rv_i](https://github.com/riscv/riscv-opcodes/blob/master/extensions/rv_i)
  e [rv_m](https://github.com/riscv/riscv-opcodes/blob/master/extensions/rv_m).

Consultadas em 2026-09-11. Implementação própria. Guias ChampionCHIP têm prioridade
para arquitetura/entregáveis; os padrões esclarecem semântica da ISA.

## Complemento recebido em 20/10/2026

- Mensagens atribuídas à organização, transcritas pelo usuário, de 19/10
  (firmware assembly para IMEM) e 20/10 (CRC-16-CCITT-FALSE, 8/16/32 bits de dados).
  [Registro, limites e comparação com a implementação](clarifications_20261020.md).
- PDF local relido: mesmo arquivo de 24 páginas, SHA-256
  `3107f22f7153aca25ea8f472be4dff7474b5c6b9b5b1f0d490da190f5e85ab41`.
  O Block Guide já integra esse arquivo; não foi recebida nova edição.
- [CRC RevEng — IBM-3740/CCITT-FALSE](https://reveng.sourceforge.io/crc-catalogue/16.htm#crc.cat.crc-16-ibm-3740)
  e [Python binascii.crc_hqx](https://docs.python.org/3/library/binascii.html#binascii.crc_hqx),
  consultados em 20/10 para conferir os parâmetros e o modelo independente.
