`timescale 1ns/1ps
module tb_pc;
    reg clk=0; always #5 clk=~clk;
    reg rst=1,we=0;
    reg [31:0] next_pc=0;
    wire [31:0] value,plus4;
    integer i;
    pc dut(clk,rst,we,next_pc,value,plus4);
    task check(input [31:0] target,input enable,input [31:0] expected);
        begin
            @(negedge clk); next_pc=target; we=enable;
            @(posedge clk); #1;
            if(value!==expected || plus4!==(expected+32'd4)) $fatal(1,"PC got=%h expected=%h",value,expected);
        end
    endtask
    initial begin
        @(posedge clk); #1; if(value!==32'h00400000) $fatal(1,"reset");
        @(negedge clk); rst=0;
        for(i=1;i<=16;i=i+1) check(32'h00400000+4*i,1,32'h00400000+4*i);
        check(32'h00400100,0,32'h00400040);
        check(32'h00400100,1,32'h00400100);
        check(32'h00400000,1,32'h00400000);
        check(32'hfffffffc,1,32'hfffffffc);
        check(0,1,0);
        @(negedge clk); rst=1; next_pc=32'h1234; we=1;
        @(posedge clk); #1; if(value!==32'h00400000) $fatal(1,"reset priority");
        $display("PASS pc: sequential, hold, forward/backward targets, wrap and reset"); $finish;
    end
endmodule
