`timescale 1ns/1ps
module regfile (
    input logic clk_i, rst_i, we_i,
    input logic [4:0] rs1_i, rs2_i, rd_i,
    input logic [31:0] data_i,
    output logic [31:0] a_o, b_o
);
    reg [31:0] regs [1:31];
    integer i;
    always @(posedge clk_i) begin
        if (rst_i) begin
            for (i=1; i<32; i=i+1) regs[i] <= 32'b0;
        end else if (we_i && rd_i != 0) regs[rd_i] <= data_i;
    end
    assign a_o = rs1_i == 0 ? 32'b0 : regs[rs1_i];
    assign b_o = rs2_i == 0 ? 32'b0 : regs[rs2_i];
endmodule
