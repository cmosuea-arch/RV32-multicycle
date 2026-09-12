# CRC — NOT DONE

## Objetivo
Extensão Xicrc, Block Guide tabelas 8 e 11, PDF pp.12,14–15.
## Entradas
rs1/rs2 de 32 bits; seletor de operação 0/1/2. Papel de cada operando pendente.
## Saídas
Resultado CRC de 16 bits; preenchimento de rd[31:16] pendente.
## Comportamento
CRCB/CRCH/CRCW processam 8/16/32 bits e produzem CRC-16 combinacional.
Opcode 0110011, funct7 1000000, funct3 000/001/010 respectivamente.
Polinômio, seed, reflexão, ordenação e xor final não definidos no guia fornecido.
## Dependências
Definição oficial complementar, decoder, datapath e writeback.
## Casos especiais
Não selecionar uma variante CRC conhecida por aproximação.
## Diagrama
Proposta arquitetural em architecture/block_diagram.md; módulo não implementado.
## Testbench
Não há TB funcional nem RTL placeholder. Decoder rejeita essas codificações;
tb_decoder e tb_core_faults verificam rejeição sem writeback.
## Casos testados
Somente rejeição como operação ainda não suportada; não conta como cobertura CRC.
## Resultado
0/3, PENDENTE.
## Integração
Pendente até contrato funcional confirmado.
## Commit validado
Nenhum commit de implementação CRC. Pendência registrada em rtl-subset-v0.1.
## Pendências
Ver architecture/official_questions.md, item 1.
