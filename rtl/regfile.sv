`timescale 1ns/1ps
// Banco de 32 registradores: duas leituras combinacionais e uma escrita síncrona.
module regfile (
    input logic clk_i, rst_i, we_i,
    input logic [4:0] rs1_i, rs2_i, rd_i,
    input logic [31:0] data_i,
    output logic [31:0] a_o, b_o
);
    // x0 não ocupa armazenamento; sua leitura é forçada a zero nos muxes abaixo.
    reg [31:0] regs [1:31];
    integer i;
    // Reset zera x1..x31; we só aceita escrita se rd não for x0.
    always @(posedge clk_i) begin
        if (rst_i) begin
            for (i=1; i<32; i=i+1) regs[i] <= 32'b0;
        end else if (we_i && rd_i != 0) regs[rd_i] <= data_i;
    end
    // rs1/rs2 são índices; a/b são os valores enviados às unidades de execução.
    assign a_o = rs1_i == 0 ? 32'b0 : regs[rs1_i];
    assign b_o = rs2_i == 0 ? 32'b0 : regs[rs2_i];
endmodule
