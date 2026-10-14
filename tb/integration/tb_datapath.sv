`timescale 1ns/1ps
// Progressive integration harness: operand mux -> ALU -> writeback register.
module tb_datapath;
    // Bancada parcial: mux escolhe B, ALU calcula e registro de writeback captura a saída.
    reg clk = 0;
    always #5 clk = ~clk;
    reg [31:0] source_a, source_b, immediate, writeback;
    reg use_imm, we;
    reg [3:0] op;
    wire [31:0] result;
    alu dut(.a_i(source_a), .b_i(use_imm ? immediate : source_b),
            .op_i(op), .result_o(result));
    always @(posedge clk) if (we) writeback <= result;
    initial begin
        // Caminho registrador: 10 + 7; #1 espera a escrita não bloqueante do writeback.
        source_a=10; source_b=7; immediate=32'hffffffff; op=1; use_imm=0; we=1;
        @(posedge clk); #1;
        if (writeback !== 17) $fatal(1, "register operand path");
        @(negedge clk); source_a=writeback; use_imm=1;
        // Caminho imediato: consome o resultado anterior e soma -1, produzindo 16.
        @(posedge clk); #1;
        if (writeback !== 16) $fatal(1, "immediate operand path");
        @(negedge clk); we=0; source_a=0;
        // Sem enable, mudar operandos não pode alterar o valor já registrado.
        @(posedge clk); #1;
        if (writeback !== 16) $fatal(1, "writeback enable");
        $display("PASS datapath: ALU operand mux and writeback");
        $finish;
    end
endmodule
