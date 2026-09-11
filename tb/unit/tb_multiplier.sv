`timescale 1ns/1ps
module tb_multiplier;
    reg [31:0] a,b,expected;
    reg [3:0] op;
    wire [31:0] result;
    integer fd,status,n;
    multiplier dut(a,b,op,result);
    initial begin
        fd=$fopen("build/multiplier.vec","r"); n=0;
        if(!fd) $fatal(1,"missing multiplier vectors");
        while(!$feof(fd)) begin
            status=$fscanf(fd,"%h %h %h %h\n",a,b,op,expected);
            if(status!=4) $fatal(1,"bad vector");
            #1; if(result!==expected) $fatal(1,"multiply op=%h a=%h b=%h got=%h expected=%h",op,a,b,result,expected);
            n=n+1;
        end
        if(n<10000) $fatal(1,"insufficient vectors");
        $display("PASS multiplier: %0d signed/mixed/unsigned high/low vectors",n); $finish;
    end
endmodule
