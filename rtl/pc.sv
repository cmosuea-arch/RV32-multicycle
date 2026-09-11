`timescale 1ns/1ps
module pc #(parameter [31:0] RESET_PC=32'h00400000) (
    input logic clk_i,rst_i,we_i,
    input logic [31:0] next_i,
    output logic [31:0] pc_o,plus4_o
);
    always @(posedge clk_i)
        if(rst_i) pc_o <= RESET_PC;
        else if(we_i) pc_o <= next_i;
    assign plus4_o=pc_o+32'd4;
endmodule
