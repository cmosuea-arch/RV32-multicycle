`timescale 1ns/1ps
module imm_ext(input logic [31:0] instr_i, output logic [31:0] imm_o);
    function automatic [31:0] extend(input [31:0] ins);
        begin
        case (ins[6:0])
            7'h03,7'h13,7'h67: extend={{20{ins[31]}},ins[31:20]};
            7'h23: extend={{20{ins[31]}},ins[31:25],ins[11:7]};
            7'h63: extend={{19{ins[31]}},ins[31],ins[7],ins[30:25],ins[11:8],1'b0};
            7'h17,7'h37: extend={ins[31:12],12'b0};
            7'h6f: extend={{11{ins[31]}},ins[31],ins[19:12],ins[20],ins[30:21],1'b0};
            default: extend=0;
        endcase
        end
    endfunction
    assign imm_o = extend(instr_i);
endmodule
