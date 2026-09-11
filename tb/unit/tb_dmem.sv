`timescale 1ns/1ps
module tb_dmem;
    reg clk=0; always #5 clk=~clk;
    reg [31:0] address=32'h10010000,data=0;
    reg oe=0,we=0;
    reg [3:0] bw=0;
    wire [31:0] q;
    reg [31:0] model[0:15];
    reg [31:0] old;
    integer i,j,k,checks;
    dmem #(.WORDS(16)) dut(clk,address,oe,we,bw,data,q);
    initial begin
        checks=0;
        for(i=0;i<16;i=i+1) begin
            @(negedge clk); address=32'h10010000+4*i; we=1; bw=15; data=32'h89abcdef^i;
            @(posedge clk); #1; model[i]=data;
        end
        for(i=0;i<16;i=i+1) for(j=0;j<16;j=j+1) begin
            @(negedge clk); address=32'h10010000+4*i; oe=1; we=1; bw=j[3:0]; data=32'h12345678^j;
            old=model[i];
            @(posedge clk); #1;
            if(q!==old) $fatal(1,"read-first index=%0d mask=%h",i,bw);
            for(k=0;k<4;k=k+1) if(bw[k]) model[i][8*k+:8]=data[8*k+:8];
            @(negedge clk); we=0;
            @(posedge clk); #1; if(q!==model[i]) $fatal(1,"masked write");
            checks=checks+1;
        end
        @(negedge clk); oe=0; old=q; address=32'h10010000;
        @(posedge clk); #1; if(q!==old) $fatal(1,"output hold");
        @(negedge clk); oe=1; address=32'h10010040; we=1; bw=15; data=0;
        @(posedge clk); #1; if(q!==0) $fatal(1,"range guard");
        @(negedge clk); we=0; address=32'h10010000;
        @(posedge clk); #1; if(q!==model[0]) $fatal(1,"out of range alias");
        $display("PASS dmem: %0d address/mask combinations, read-first, hold and bounds",checks); $finish;
    end
endmodule
