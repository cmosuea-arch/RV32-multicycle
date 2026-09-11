`timescale 1ns/1ps
module branch_comp(input logic [31:0] a_i,b_i,input logic [2:0] funct3_i,output wire taken_o);
    function automatic compare(input [31:0] a,b,input [2:0] f);
        case(f)
            0: compare=a==b;
            1: compare=a!=b;
            4: compare=$signed(a)<$signed(b);
            5: compare=$signed(a)>=$signed(b);
            6: compare=a<b;
            7: compare=a>=b;
            default: compare=0;
        endcase
    endfunction
    assign taken_o=compare(a_i,b_i,funct3_i);
endmodule
