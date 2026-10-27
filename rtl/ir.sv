`timescale 1ns/1ps
// Guarda a instrução buscada para mantê-la estável ao longo dos vários estados.
module ir(input logic clk_i,rst_i,we_i,input logic [31:0] instr_i,output logic [31:0] instr_o);
    // Reset síncrono zera; we captura em FETCH; sem we mantém o valor anterior.
    // O decoder vê este registro, sem depender de alterações posteriores no barramento.
    always @(posedge clk_i)
        if(rst_i) instr_o<=0;
        else if(we_i) instr_o<=instr_i;
endmodule
