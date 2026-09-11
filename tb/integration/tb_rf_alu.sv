`timescale 1ns/1ps
module tb_rf_alu;
    reg clk=0;
    always #5 clk=~clk;
    reg rst=1,we=0,imm_sel=1;
    reg [4:0] rs1=0,rs2=0,rd=0;
    reg [3:0] op=0;
    reg [31:0] instr=0;
    wire [31:0] imm;
    imm_ext immediate_i(instr,imm);
    wire [31:0] a,b,result;
    regfile rf(clk,rst,we,rs1,rs2,rd,result,a,b);
    alu alu_i(a,imm_sel?imm:b,op,result);
    initial begin
        @(posedge clk); #1;
        @(negedge clk); rst=0; we=1; rd=1; instr=32'hfff00013;
        @(posedge clk); #1;
        @(negedge clk); rd=2; instr=32'h00100013;
        @(posedge clk); #1;
        @(negedge clk); rd=3; rs1=1; rs2=2; imm_sel=0; op=1;
        @(posedge clk); #1;
        @(negedge clk); we=0; rs1=3; #1;
        if(a !== 0) $fatal(1,"RF ALU modular ADD");
        @(negedge clk); we=1; rd=1; rs1=1; op=2;
        @(posedge clk); #1;
        if(a !== 32'hfffffffe) $fatal(1,"RF ALU dependent SUB");
        $display("PASS rf_alu: source reads, overflow and dependent writeback"); $finish;
    end
endmodule
