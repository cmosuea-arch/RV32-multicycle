`timescale 1ns/1ps
module tb_address_decoder;
    reg [31:0] addr=0,din=32'h12345678;
    reg oe=0,we=0;
    reg [3:0] bw=0;
    wire [31:0] ma,md,dout;
    wire io,doe,dwe,fault;
    wire [3:0] dbw;
    reg [31:0] addresses[0:11];
    reg ih,dh;
    integer i,o,w,b,n;
    address_decoder #(.IMEM_WORDS(8),.DMEM_WORDS(8)) dut(addr,din,oe,we,bw,32'habc,32'hdef,ma,md,dout,io,doe,dwe,dbw,fault);
    initial begin
        addresses[0]=0; addresses[1]=32'h003fffff; addresses[2]=32'h00400000;
        addresses[3]=32'h00400003; addresses[4]=32'h0040001f; addresses[5]=32'h00400020;
        addresses[6]=32'h1000ffff; addresses[7]=32'h10010000; addresses[8]=32'h10010003;
        addresses[9]=32'h1001001f; addresses[10]=32'h10010020; addresses[11]=32'hffffffff;
        n=0;
        for(i=0;i<12;i=i+1) for(o=0;o<2;o=o+1) for(w=0;w<2;w=w+1) for(b=0;b<16;b=b+1) begin
            addr=addresses[i]; oe=o[0]; we=w[0]; bw=b[3:0];
            ih=(i>=2&&i<=4); dh=(i>=7&&i<=9); #1;
            if(ma!=={addr[31:2],2'b0}||md!==din||io!==(oe&&ih&&!we)||doe!==(oe&&dh)||dwe!==(we&&dh)) $fatal(1,"routing %h",addr);
            if(dbw!==((we&&dh)?bw:4'b0)||fault!==((oe||we)&&(!(ih||dh)||(we&&ih)))) $fatal(1,"gating %h",addr);
            if(dout!==((oe&&ih&&!we)?32'habc:(oe&&dh)?32'hdef:32'b0)) $fatal(1,"return mux");
            n=n+1;
        end
        $display("PASS address_decoder: %0d boundary/request/mask combinations",n); $finish;
    end
endmodule
