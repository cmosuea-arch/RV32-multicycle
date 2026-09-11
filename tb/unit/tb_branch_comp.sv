`timescale 1ns/1ps
module tb_branch_comp;
    reg [31:0] a,b;
    reg [2:0] f;
    reg expected;
    wire taken;
    integer fd,status,n;
    branch_comp dut(a,b,f,taken);
    initial begin
        fd=$fopen("build/branch.vec","r"); n=0;
        if(!fd) $fatal(1,"missing branch vectors");
        while(!$feof(fd)) begin
            status=$fscanf(fd,"%h %h %h %h\n",a,b,f,expected);
            if(status!=4) $fatal(1,"bad vector");
            #1; if(taken!==expected) $fatal(1,"branch f=%h a=%h b=%h",f,a,b);
            n=n+1;
        end
        if(n<9000) $fatal(1,"insufficient vectors");
        $display("PASS branch_comp: %0d signed/unsigned vectors",n); $finish;
    end
endmodule
