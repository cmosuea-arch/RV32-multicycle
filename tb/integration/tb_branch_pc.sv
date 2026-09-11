`timescale 1ns/1ps
module tb_branch_pc;
    reg clk=0; always #5 clk=~clk;
    reg rst=1,we=0;
    reg [31:0] a=1,b=1,instr=32'h00000463;
    wire taken;
    wire [31:0] current_pc,plus4,imm,target;
    branch_comp bc(a,b,3'b000,taken);
    imm_ext x(instr,imm);
    alu al(current_pc,imm,4'h1,target);
    pc p(clk,rst,we,taken?target:plus4,current_pc,plus4);
    initial begin
        @(posedge clk); #1; @(negedge clk); rst=0; we=1;
        @(posedge clk); #1; if(current_pc!==32'h00400008) $fatal(1,"taken");
        @(negedge clk); b=2;
        @(posedge clk); #1; if(current_pc!==32'h0040000c) $fatal(1,"not taken");
        @(negedge clk); b=1; instr=32'hfe000ce3;
        @(posedge clk); #1; if(current_pc!==32'h00400004) $fatal(1,"backward");
        $display("PASS branch_pc: taken/not-taken and forward/backward redirects"); $finish;
    end
endmodule
