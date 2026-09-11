`timescale 1ns/1ps
module decoder(
    input logic [31:0] instr_i,
    output reg [3:0] alu_op_o,
    output reg a_pc_o,b_imm_o,reg_we_o,branch_o,jal_o,jalr_o,load_o,store_o,mul_o,illegal_o
);
    always @* begin
        alu_op_o=0; a_pc_o=0; b_imm_o=0; reg_we_o=0;
        branch_o=0; jal_o=0; jalr_o=0; load_o=0; store_o=0; mul_o=0;
        illegal_o=0;
        case(instr_i[6:0])
            7'h33: begin
                reg_we_o=1;
                if(instr_i[31:25]==0) begin
                    case(instr_i[14:12])
                        0: alu_op_o=1; 1: alu_op_o=6; 2: alu_op_o=9; 3: alu_op_o=10;
                        4: alu_op_o=5; 5: alu_op_o=7; 6: alu_op_o=4; 7: alu_op_o=3;
                    endcase
                end else if(instr_i[31:25]==7'h20 && instr_i[14:12]==0) alu_op_o=2;
                else if(instr_i[31:25]==7'h20 && instr_i[14:12]==5) alu_op_o=8;
                else illegal_o=1;
            end
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
            default: illegal_o=1;
        endcase
        if(illegal_o) begin
            alu_op_o=0; a_pc_o=0; b_imm_o=0; reg_we_o=0;
            branch_o=0; jal_o=0; jalr_o=0; load_o=0; store_o=0; mul_o=0;
        end
    end
endmodule
