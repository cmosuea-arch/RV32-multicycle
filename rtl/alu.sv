`timescale 1ns/1ps
// Recebe dois operandos de 32 bits e um código interno fornecido pelo decoder.
module alu (
    input  logic [31:0] a_i, b_i,
    input  logic [3:0]  op_i,
    output logic [31:0] result_o
);
    // Lógica combinacional: o seletor escolhe a operação sem armazenar estado.
    function automatic [31:0] evaluate(input [31:0] a, b, input [3:0] op);
        begin
        case (op)
            // PASS_B serve a LUI; soma/subtração descartam o carry além de 32 bits.
            4'h0: evaluate = b;
            4'h1: evaluate = a + b;
            4'h2: evaluate = a - b;
            4'h3: evaluate = a & b;
            4'h4: evaluate = a | b;
            4'h5: evaluate = a ^ b;
            // RV32 usa cinco bits para deslocar de 0 a 31 posições.
            4'h6: evaluate = a << b[4:0];
            4'h7: evaluate = a >> b[4:0];
            // $signed preserva o sinal no SRA e distingue SLT de SLTU.
            4'h8: evaluate = $signed(a) >>> b[4:0];
            4'h9: evaluate = {31'b0, $signed(a) < $signed(b)};
            4'ha: evaluate = {31'b0, a < b};
            default: evaluate = 32'b0;
        endcase
        end
    endfunction
    // A saída acompanha as entradas; quem armazena o resultado é o core.
    assign result_o = evaluate(a_i, b_i, op_i);
endmodule
