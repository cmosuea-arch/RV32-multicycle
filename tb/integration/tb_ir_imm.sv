`timescale 1ns/1ps
module tb_ir_imm;
    // Verifica se a instrução retida no IR mantém estável o imediato usado pela ALU.
    reg clk=0; always #5 clk=~clk;
    reg rst=1,we=0;
    reg [31:0] din=0;
    wire [31:0] instruction,imm,result;
    ir r(clk,rst,we,din,instruction);
    imm_ext x(instruction,imm);
    alu a(32'd10,imm,4'h1,result);
    initial begin
        // Captura uma instrução com imediato -1: a ALU deve calcular 10 + (-1) = 9.
        @(posedge clk); #1;
        @(negedge clk); rst=0; we=1; din=32'hfff00013;
        @(posedge clk); #1; if(result!==9) $fatal(1,"IR to immediate/ALU");
        @(negedge clk); we=0; din=32'h00100013;
        // Mudar din sem habilitar o IR não pode trocar o operando nem o resultado.
        @(posedge clk); #1; if(result!==9) $fatal(1,"IR retention stabilizes operands");
        $display("PASS ir_imm: captured instruction and stable execution operand"); $finish;
    end
endmodule
