`timescale 1ns/1ps
module ir(input logic clk_i,rst_i,we_i,input logic [31:0] instr_i,output logic [31:0] instr_o);
    always @(posedge clk_i)
        if(rst_i) instr_o<=0;
        else if(we_i) instr_o<=instr_i;
endmodule
