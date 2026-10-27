# Contratos CMOS v1

Convenção: `snake_case`, módulos sem prefixo, entradas `_i`, saídas `_o`, estado
registrado `_q`. Dados, instruções e endereços: 32 bits; índices RF: 5 bits.
Clock na borda de subida; reset `rst_i` síncrono ativo alto. Enables ativos altos.
Interfaces abaixo são decisões CMOS onde o guia não especifica portas completas.

| Módulo | Entradas | Saídas / contrato |
|---|---|---|
| alu | a_i[31:0], b_i[31:0], op_i[3:0] | result_o[31:0], combinacional; tabela 9 |
| regfile | clk_i, rst_i, we_i, rs1_i[4:0], rs2_i[4:0], rd_i[4:0], data_i[31:0] | a_o/b_o[31:0]; leitura assíncrona, escrita síncrona, x0=0 |
| imm_ext | instr_i[31:0] | imm_o[31:0]; formato por opcode |
| pc | clk_i, rst_i, we_i, next_i[31:0] | pc_o[31:0], plus4_o[31:0]; RESET_PC=0x00400000 |
| ir | clk_i, rst_i, we_i, instr_i[31:0] | instr_o[31:0] |
| imem | address_i[31:0] absoluto alinhado, oe_i | data_o[31:0]; ROM combinacional; WORDS e INIT_FILE |
| branch_comp | a_i/b_i[31:0], funct3_i[2:0] | taken_o |
| lsu | address_i, store_i, mem_i[31:0], funct3_i[2:0], is_store_i | load_o, store_o[31:0], bw_o[3:0], misaligned_o, invalid_o |
| dmem | clk_i, address_i[31:0] absoluto, oe_i, we_i, bw_i[3:0], data_i[31:0] | data_o[31:0]; leitura/escrita síncronas; read-first |
| address_decoder | address_i, data_i[31:0], oe_i, we_i, bw_i[3:0], imem_data_i/dmem_data_i[31:0] | mem_address_o, mem_data_o, data_o[31:0], imem_oe_o, dmem_oe_o, dmem_we_o, dmem_bw_o[3:0], fault_o |
| multiplier | a_i/b_i[31:0], op_i[3:0] | result_o[31:0]; tabela 10 |
| control_unit | clk_i, rst_i, illegal_i, load_i, store_i, fault_i | state_o[2:0] |
| decoder | instr_i[31:0] | alu_op_o[3:0], a_pc_o, b_imm_o, reg_we_o, branch_o, jal_o, jalr_o, load_o, store_o, mul_o, illegal_o, crc_o |
| crc | a_i[31:0]=dados, b_i[15:0]=CRC anterior, op_i[3:0] | result_o[31:0]; CRC16/0x1021, bytes mais significativos primeiro |
| riscv_core | clk_i, rst_i, data_i[31:0], bus_fault_i | address_o/data_o[31:0], oe_o, we_o, bw_o[3:0], fault_o, commit_valid_o, commit_pc_o/commit_instr_o/commit_data_o[31:0], commit_rd_o[4:0] |
| riscv_top | clk_i, rst_i | sinais de observação fault_o e commit_*; instancia core, decoder de endereço e memórias |
| simple_system | clk_i, rst_i | done_o, success_o, fault_o; experimento CRC, ROM 2 KiB/RAM 1 KiB |

Seleção de operandos: A=rs1 ou PC; B=rs2 ou imediato. Resultado executado é
registrado; writeback escolhe resultado ou load. Jump registra PC+4 como link.
PC e RF atualizam apenas na aposentadoria da instrução, IR apenas em FETCH.

FSM básica: FETCH → DECODE → EXECUTE → WRITEBACK → FETCH. Loads/stores acrescentam
MEMORY entre EXECUTE e WRITEBACK; DMEM captura o pedido na borda final de MEMORY.
Durante WRITEBACK o endereço efetivo e `oe` do load são mantidos, preservando a
seleção do dado lido. FAULT retém estado até reset e desativa efeitos colaterais.
Os operandos são estáveis enquanto IR não muda; RF só escreve em WRITEBACK.

CRC: [contrato oficial implementado](crc.md), validado com o firmware de 27/10.
Decoder/core/top possuem `EXPERIMENTAL_XICRC=1` por padrão; o nome histórico foi
preservado por compatibilidade. Valor 0 rejeita as três instruções. Dados vêm
de rs1, CRC anterior de rs2 e o resultado passa por EXECUTE/WRITEBACK.
