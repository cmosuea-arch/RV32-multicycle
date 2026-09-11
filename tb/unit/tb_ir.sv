`timescale 1ns/1ps
module tb_ir;
    reg clk=0; always #5 clk=~clk;
    reg rst=1,we=0;
    reg [31:0] din=32'hffffffff;
    wire [31:0] q;
    integer i;
    ir dut(clk,rst,we,din,q);
    initial begin
        @(posedge clk); #1; if(q!==0) $fatal(1,"reset");
        @(negedge clk); rst=0;
        for(i=1;i<65;i=i+1) begin
            @(negedge clk); we=1; din=32'h1234567*i;
            @(posedge clk); #1; if(q!==din) $fatal(1,"capture");
            @(negedge clk); we=0; din=~din;
            @(posedge clk); #1; if(q!==~din) $fatal(1,"hold");
        end
        @(negedge clk); rst=1; we=1;
        @(posedge clk); #1; if(q!==0) $fatal(1,"reset priority");
        $display("PASS ir: 64 capture/hold pairs and reset"); $finish;
    end
endmodule
