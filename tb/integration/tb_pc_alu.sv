`timescale 1ns/1ps
module tb_pc_alu;
    // Integra PC, imediato J e ALU para verificar cálculo de alvo relativo ao PC.
    reg clk=0; always #5 clk=~clk;
    reg rst=1,we=0,redirect=0;
    reg [31:0] instr=32'h0100006f;
    wire [31:0] current_pc,plus4,imm,target;
    pc p(clk,rst,we,redirect?target:plus4,current_pc,plus4);
    // redirect seleciona soma PC+imediato; caso contrário, segue sequencialmente.
    imm_ext x(instr,imm);
    alu a(current_pc,imm,4'h1,target);
    initial begin
        // Após reset, primeiro avança quatro bytes; depois usa offset +16 da instrução.
        @(posedge clk); #1;
        @(negedge clk); rst=0; we=1;
        @(posedge clk); #1; if(current_pc!==32'h00400004) $fatal(1,"PC+4");
        @(negedge clk); redirect=1;
        // 00400004 + 0x10 deve carregar 00400014 na próxima borda de subida.
        @(posedge clk); #1; if(current_pc!==32'h00400014) $fatal(1,"PC-relative target got=%h imm=%h",current_pc,imm);
        $display("PASS pc_alu: PC plus immediate redirect"); $finish;
    end
endmodule
