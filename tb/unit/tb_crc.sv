`timescale 1ns/1ps
module tb_crc;
    reg [31:0] a,b,expected;
    reg [3:0] op;
    wire [31:0] result;
    integer fd,status,n;
    crc dut(a,b,op,result);
    initial begin
        fd=$fopen("build/crc.vec","r"); n=0;
        if(!fd) $fatal(1,"missing CRC vectors");
        while(!$feof(fd)) begin
            status=$fscanf(fd,"%h %h %h %h\n",a,b,op,expected);
            if(status!=4) $fatal(1,"bad CRC vector");
            #1;
            if(result!==expected) $fatal(1,"CRC op=%h acc=%h data=%h got=%h expected=%h",op,a,b,result,expected);
            n=n+1;
        end
        if(n!=18304) $fatal(1,"incomplete CRC vectors");
        // Valor conhecido, independente do arquivo de vetores.
        a=32'hffff; b=32'h34333231; op=2; #1;
        a=result; b=32'h38373635; #1;
        a=result; b=32'h39; op=0; #1;
        if(result!==32'h29b1) $fatal(1,"CRC known answer failed");
        $display("PASS crc: %0d vectors and 123456789 -> 29b1 (provisional contract)",n);
        $finish;
    end
endmodule
