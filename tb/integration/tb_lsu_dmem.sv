`timescale 1ns/1ps
module tb_lsu_dmem;
    // Liga formatação/máscara da LSU a uma RAM real para testar preservação dos bytes.
    reg clk=0; always #5 clk=~clk;
    reg [31:0] address=32'h10010000,src=32'hdeadbeef;
    reg [2:0] f=2;
    reg st=1,oe=0,we=0;
    wire [31:0] ld,sd,mem;
    wire [3:0] bw;
    wire bad,invalid;
    lsu l(address,src,mem,f,st,ld,sd,bw,bad,invalid);
    dmem #(.WORDS(4)) d(clk,{address[31:2],2'b0},oe,we&&!bad&&!invalid,bw,sd,mem);
    // RAM recebe endereço alinhado; a LSU usa os bits baixos e bloqueia acessos inválidos.
    integer offset;
    initial begin
        // Inicializa uma palavra via SW; em seguida escreve 80,81,82,83 nos quatro bytes.
        @(negedge clk); we=1;
        @(posedge clk); #1;
        for(offset=0;offset<4;offset=offset+1) begin
            @(negedge clk); address=32'h10010000+offset; src=32'h80+offset; f=0; st=1;
            @(posedge clk); #1;
        end
        @(negedge clk); we=0; oe=1; st=0; f=2; address=32'h10010000;
        // Lê palavra completa e halfword com sinal, respeitando leitura síncrona da RAM.
        @(posedge clk); #1; if(ld!==32'h83828180) $fatal(1,"all byte stores");
        @(negedge clk); address=32'h10010002; f=1;
        @(posedge clk); #1; if(ld!==32'hffff8382) $fatal(1,"signed halfword");
        @(negedge clk); st=1; we=1; oe=0; src=32'h1234; f=1;
        // SH altera só a metade alta; a leitura seguinte deve preservar os bytes baixos.
        @(posedge clk); #1;
        @(negedge clk); we=0; st=0; oe=1; address=32'h10010000; f=2;
        @(posedge clk); #1; if(ld!==32'h12348180) $fatal(1,"preserved bytes");
        $display("PASS lsu_dmem: SW/SB/SH, byte preservation and load formatting"); $finish;
    end
endmodule
