`timescale 1ns/1ps
module imm_ext(input logic [31:0] instr_i, output logic [31:0] imm_o);
    always @* begin
        case (instr_i[6:0])
            7'h03,7'h13,7'h67: imm_o={{20{instr_i[31]}},instr_i[31:20]};
            7'h23: imm_o={{20{instr_i[31]}},instr_i[31:25],instr_i[11:7]};
            7'h63: imm_o={{19{instr_i[31]}},instr_i[31],instr_i[7],instr_i[30:25],instr_i[11:8],1'b0};
            7'h17,7'h37: imm_o={instr_i[31:12],12'b0};
            7'h6f: imm_o={{11{instr_i[31]}},instr_i[31],instr_i[19:12],instr_i[20],instr_i[30:21],1'b0};
            default: imm_o=0;
        endcase
    end
endmodule
