`timescale 1ns/1ps
// Zmmul combinacional: op=0 MUL, 1 MULH, 2 MULHSU, 3 MULHU; não implementa divisão.
module multiplier(input logic [31:0] a_i,b_i,input logic [3:0] op_i,output wire [31:0] result_o);
    // O 33º bit permite representar cada operando como signed ou unsigned.
    wire signed [32:0] a_ext={(op_i<3)&&a_i[31],a_i};
    wire signed [32:0] b_ext={(op_i<2)&&b_i[31],b_i};
    wire signed [65:0] product=a_ext*b_ext;
    // MUL devolve a metade baixa; as outras operações devolvem os bits 63:32.
    assign result_o=op_i==0 ? product[31:0] : op_i<=3 ? product[63:32] : 32'b0;
endmodule
