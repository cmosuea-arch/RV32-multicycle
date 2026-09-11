`timescale 1ns/1ps
module tb_lsu;
    reg [31:0] addr,src,mem,eld,esd;
    reg [2:0] f;
    reg st,ebad,einvalid;
    reg [3:0] ebw;
    wire [31:0] ld,sd;
    wire [3:0] bw;
    wire bad,invalid;
    integer fd,status,n;
    lsu dut(addr,src,mem,f,st,ld,sd,bw,bad,invalid);
    initial begin
        fd=$fopen("build/lsu.vec","r"); n=0;
        if(!fd) $fatal(1,"missing LSU vectors");
        while(!$feof(fd)) begin
            status=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h\n",addr,src,mem,f,st,eld,esd,ebw,ebad,einvalid);
            if(status!=10) $fatal(1,"bad vector");
            #1;
            if({ld,sd,bw,bad,invalid}!=={eld,esd,ebw,ebad,einvalid}) $fatal(1,"LSU addr=%h f=%h store=%h",addr,f,st);
            n=n+1;
        end
        if(n<8000) $fatal(1,"insufficient vectors");
        $display("PASS lsu: %0d byte/half/word, signed/unsigned, masks and invalid vectors",n); $finish;
    end
endmodule
