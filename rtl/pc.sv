`timescale 1ns/1ps
// Mantém o endereço da instrução atual; o core fornece o próximo endereço.
module pc #(parameter [31:0] RESET_PC=32'h00400000) (
    input logic clk_i,rst_i,we_i,
    input logic [31:0] next_i,
    output logic [31:0] pc_o,plus4_o
);
    // Reset síncrono ativo em 1; sem we, o PC não avança entre estados da instrução.
    // No core, we vem da aposentadoria: FAULT e TRAP conservam o PC atual.
    always @(posedge clk_i)
        if(rst_i) pc_o <= RESET_PC;
        else if(we_i) pc_o <= next_i;
    // Instruções têm quatro bytes: PC+4 serve à sequência normal e ao link de jumps.
    assign plus4_o=pc_o+32'd4;
endmodule
