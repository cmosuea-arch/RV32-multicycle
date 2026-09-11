`timescale 1ns/1ps
module tb_lsu_rf;
    reg clk=0; always #5 clk=~clk;
    reg rst=1,we=0,st=0;
    reg [2:0] f=0;
    reg [31:0] offset=2;
    wire [31:0] address,ld,sd,a,b;
    wire [3:0] bw;
    wire bad,invalid;
    alu al(32'h10010000,offset,4'h1,address);
    lsu l(address,32'h12345678,32'hf4f3f2f1,f,st,ld,sd,bw,bad,invalid);
    regfile rf(clk,rst,we,5'd1,5'd0,5'd1,ld,a,b);
    initial begin
        @(posedge clk); #1; @(negedge clk); rst=0; we=1;
        @(posedge clk); #1; if(a!==32'hfffffff3||bad||invalid) $fatal(1,"LB writeback");
        @(negedge clk); f=4;
        @(posedge clk); #1; if(a!==32'h000000f3) $fatal(1,"LBU writeback");
        @(negedge clk); we=0; st=1; f=0; #1;
        if(sd!==32'h00780000||bw!==4'b0100) $fatal(1,"SB position");
        $display("PASS lsu_rf: effective address, signed/unsigned RF writeback and store lanes"); $finish;
    end
endmodule
