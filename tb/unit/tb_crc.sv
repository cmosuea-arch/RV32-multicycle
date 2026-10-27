`timescale 1ns/1ps
module tb_crc;
    // Verifica dados em a/rs1, acumulador em b/rs2 e os três tamanhos do contrato oficial.
    reg [31:0] a,b,expected;
    reg [3:0] op;
    wire [31:0] result;
    integer fd,status,n,size,i;
    reg [63:0] official_message=64'h1234567890abcdef;
    crc dut(a,b,op,result);
    initial begin
        // A referência usa binascii.crc_hqx; seletores inválidos também estão nos vetores.
        fd=$fopen("build/crc.vec","r"); n=0;
        if(!fd) $fatal(1,"missing CRC vectors");
        while(!$feof(fd)) begin
            // Lê um caso e compara o resultado de 32 bits após estabilização da lógica.
            status=$fscanf(fd,"%h %h %h %h\n",a,b,op,expected);
            if(status!=4) $fatal(1,"bad CRC vector");
            #1;
            if(result!==expected) $fatal(1,"CRC op=%h data=%h acc=%h got=%h expected=%h",op,a,b,result,expected);
            n=n+1;
        end
        if(n!=18304) $fatal(1,"incomplete CRC vectors");
        // Valor conhecido, independente do arquivo de vetores.
        b=32'hffff; a=32'h31323334; op=2; #1;
        b=result; a=32'h35363738; #1;
        // Reutiliza o CRC anterior: duas palavras e um byte formam "123456789".
        b=result; a=32'h39; op=0; #1;
        if(result!==32'h29b1) $fatal(1,"CRC known answer failed");
        // Os três agrupamentos do firmware oficial devem dar 00001E82.
        for(size=1;size<=4;size=size*2) begin
            b=32'habcdffff; op=(size==1)?0:(size==2)?1:2;
            for(i=0;i<8;i=i+size) begin
                a=32'(official_message>>((8-size-i)*8)); #1;
                b=result;
            end
            if(result!==32'h1e82) $fatal(1,"official CRC size=%0d got=%h",size,result);
        end
        $display("PASS crc: %0d vectors, ASCII -> 29b1, official byte/half/word -> 1e82",n);
        $finish;
    end
endmodule
