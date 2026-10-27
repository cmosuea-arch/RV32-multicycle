`timescale 1ns/1ps
// Traduz opcode/funct3/funct7 em seletores do datapath e classes para a FSM.
// EXPERIMENTAL_XICRC é o nome histórico do parâmetro; o padrão inclui Xicrc oficial.
module decoder #(
    parameter bit EXPERIMENTAL_XICRC=1
)(
    input logic [31:0] instr_i,
    output reg [3:0] alu_op_o,
    output reg a_pc_o,b_imm_o,reg_we_o,branch_o,jal_o,jalr_o,load_o,store_o,mul_o,illegal_o,
    output reg crc_o
);
    // Defaults em todos os caminhos evitam latches na lógica combinacional.
    always @* begin
        alu_op_o=0; a_pc_o=0; b_imm_o=0; reg_we_o=0;
        branch_o=0; jal_o=0; jalr_o=0; load_o=0; store_o=0; mul_o=0;
        illegal_o=0; crc_o=0;
        case(instr_i[6:0])
            // OP: operações entre registradores, Zmmul e Xicrc.
            7'h33: begin
                reg_we_o=1;
                if(instr_i[31:25]==0) begin
                    case(instr_i[14:12])
                        0: alu_op_o=1; 1: alu_op_o=6; 2: alu_op_o=9; 3: alu_op_o=10;
                        4: alu_op_o=5; 5: alu_op_o=7; 6: alu_op_o=4; 7: alu_op_o=3;
                    endcase
                end else if(instr_i[31:25]==7'h20 && instr_i[14:12]==0) alu_op_o=2;
                else if(instr_i[31:25]==7'h20 && instr_i[14:12]==5) alu_op_o=8;
                else if(instr_i[31:25]==7'h01 && instr_i[14:12]<=3) begin mul_o=1; alu_op_o=0; end
                else if(EXPERIMENTAL_XICRC && instr_i[31:25]==7'h40 && instr_i[14:12]<=2) crc_o=1;
                else illegal_o=1;
            end
            // OP-IMM: operando B vem do imediato; shifts também validam funct7.
            7'h13: begin
                reg_we_o=1; b_imm_o=1;
                case(instr_i[14:12])
                    0: alu_op_o=1;
                    1: begin alu_op_o=6; if(instr_i[31:25]!=0) illegal_o=1; end
                    2: alu_op_o=9;
                    3: alu_op_o=10;
                    4: alu_op_o=5;
                    5: begin
                        if(instr_i[31:25]==0) alu_op_o=7;
                        else if(instr_i[31:25]==7'h20) alu_op_o=8;
                        else illegal_o=1;
                    end
                    6: alu_op_o=4;
                    7: alu_op_o=3;
                endcase
            end
            // LUI passa o imediato; AUIPC soma esse imediato ao PC atual.
            7'h37: begin reg_we_o=1; b_imm_o=1; alu_op_o=0; end
            7'h17: begin reg_we_o=1; b_imm_o=1; a_pc_o=1; alu_op_o=1; end
            // Branch usa PC+imediato como alvo; branch_comp decide se ele é usado.
            7'h63: begin
                branch_o=1; a_pc_o=1; b_imm_o=1; alu_op_o=1;
                if(instr_i[14:12]==2 || instr_i[14:12]==3) illegal_o=1;
            end
            // JAL/JALR calculam o alvo na ALU; o core grava PC+4 em rd.
            7'h6f: begin jal_o=1; reg_we_o=1; a_pc_o=1; b_imm_o=1; alu_op_o=1; end
            7'h67: begin
                jalr_o=1; reg_we_o=1; b_imm_o=1; alu_op_o=1;
                if(instr_i[14:12]!=0) illegal_o=1;
            end
            // Load/store somam rs1+imediato; a LSU interpreta tamanho e sinal.
            7'h03: begin
                load_o=1; reg_we_o=1; b_imm_o=1; alu_op_o=1;
                if(!(instr_i[14:12]==0||instr_i[14:12]==1||instr_i[14:12]==2||instr_i[14:12]==4||instr_i[14:12]==5)) illegal_o=1;
            end
            7'h23: begin
                store_o=1; b_imm_o=1; alu_op_o=1;
                if(instr_i[14:12]>2) illegal_o=1;
            end
            default: illegal_o=1;
        endcase
        // Instruções inválidas anulam controles para não causar escrita ou salto.
        if(illegal_o) begin
            alu_op_o=0; a_pc_o=0; b_imm_o=0; reg_we_o=0;
            branch_o=0; jal_o=0; jalr_o=0; load_o=0; store_o=0; mul_o=0;
            crc_o=0;
        end
    end
endmodule
