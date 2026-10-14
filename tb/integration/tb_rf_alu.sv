`timescale 1ns/1ps
module tb_rf_alu;
    // A saída da ALU retorna à porta de escrita do RF para testar operações dependentes.
    // Clock de 10 ns; estímulos mudam na descida e escritas ocorrem na subida.
    reg clk=0;
    always #5 clk=~clk;
    reg rst=1,we=0,imm_sel=1;
    reg [4:0] rs1=0,rs2=0,rd=0;
    reg [3:0] op=0;
    reg [31:0] instr=0;
    wire [31:0] imm;
    // O imediato inicializa o RF pela ALU; depois a ALU lê dois registradores.
    imm_ext immediate_i(instr,imm);
    wire [31:0] a,b,result;
    regfile rf(clk,rst,we,rs1,rs2,rd,result,a,b);
    alu alu_i(a,imm_sel?imm:b,op,result);
    initial begin
        // Reset primeiro; #1 após cada subida espera a atualização dos registradores.
        @(posedge clk); #1;
        // PASS_B grava -1 em x1 e 1 em x2 a partir dos imediatos.
        @(negedge clk); rst=0; we=1; rd=1; instr=32'hfff00013;
        @(posedge clk); #1;
        @(negedge clk); rd=2; instr=32'h00100013;
        @(posedge clk); #1;
        // ADD deve dar zero em 32 bits; SUB testa destino igual à fonte x1.
        @(negedge clk); rd=3; rs1=1; rs2=2; imm_sel=0; op=1;
        @(posedge clk); #1;
        @(negedge clk); we=0; rs1=3; #1;
        // Desabilita escrita antes de ler x3, evitando modificar o resultado observado.
        if(a !== 0) $fatal(1,"RF ALU modular ADD");
        @(negedge clk); we=1; rd=1; rs1=1; op=2;
        @(posedge clk); #1;
        if(a !== 32'hfffffffe) $fatal(1,"RF ALU dependent SUB");
        $display("PASS rf_alu: source reads, overflow and dependent writeback"); $finish;
    end
endmodule
