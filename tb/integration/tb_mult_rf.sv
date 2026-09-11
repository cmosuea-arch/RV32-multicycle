`timescale 1ns/1ps
module tb_mult_rf;
    reg clk=0; always #5 clk=~clk;
    reg rst=1,we=0,preload=1;
    reg [4:0] rd=1,rs1=1;
    reg [3:0] op=2;
    wire [31:0] a,b,product;
    regfile rf(clk,rst,we,rs1,5'd2,rd,preload?32'hffffffff:product,a,b);
    multiplier m(a,b,op,product);
    initial begin
        @(posedge clk); #1; @(negedge clk); rst=0; we=1;
        @(posedge clk); #1; @(negedge clk); rd=2;
        @(posedge clk); #1; @(negedge clk); preload=0; rd=3;
        @(posedge clk); #1; @(negedge clk); we=0; rs1=3; #1;
        if(a!==32'hffffffff) $fatal(1,"MULHSU writeback");
        @(negedge clk); rs1=1; we=1; op=3;
        @(posedge clk); #1; @(negedge clk); we=0; rs1=3; #1;
        if(a!==32'hfffffffe) $fatal(1,"MULHU writeback");
        $display("PASS mult_rf: mixed/unsigned high product writeback"); $finish;
    end
endmodule
