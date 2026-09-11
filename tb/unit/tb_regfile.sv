`timescale 1ns/1ps
module tb_regfile;
    reg clk=0;
    always #5 clk=~clk;
    reg rst=1, we=0;
    reg [4:0] rs1=0, rs2=0, rd=0;
    reg [31:0] data=0;
    wire [31:0] a,b;
    integer i,j;
    reg [31:0] expected [0:31];
    regfile dut(clk,rst,we,rs1,rs2,rd,data,a,b);
    initial begin
        for(i=0;i<32;i=i+1) expected[i]=0;
        @(posedge clk); #1;
        @(negedge clk); rst=0;
        for(i=0;i<32;i=i+1) begin
            rs1=i[4:0]; rs2=i[4:0]; #1;
            if(a !== 0 || b !== 0) $fatal(1,"reset x%0d",i);
        end
        for(i=0;i<32;i=i+1) begin
            @(negedge clk); we=1; rd=i[4:0]; rs1=i[4:0]; data=32'h80000000 ^ (32'h1234567*i);
            #1; if(a !== 0) $fatal(1,"write before clock");
            @(posedge clk); #1;
            if(i!=0) expected[i]=data;
            if(a !== expected[i]) $fatal(1,"write x%0d",i);
        end
        @(negedge clk); we=0; data=0;
        for(i=0;i<32;i=i+1) for(j=0;j<32;j=j+1) begin
            rs1=i[4:0]; rs2=j[4:0]; #1;
            if(a !== expected[i] || b !== expected[j]) $fatal(1,"dual read %0d/%0d",i,j);
        end
        @(negedge clk); rst=1; we=1; rd=5; data=32'hffffffff; rs1=5;
        @(posedge clk); #1;
        if(a !== 0) $fatal(1,"reset priority");
        $display("PASS regfile: 32 writes, 1024 dual reads, x0, enables and reset"); $finish;
    end
endmodule
