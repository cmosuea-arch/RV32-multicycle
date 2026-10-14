`timescale 1ns/1ps
module tb_memory_bus;
    // Integra decoder de endereços com ROM/RAM para conferir pedidos e retorno de dados.
    reg clk=0; always #5 clk=~clk;
    reg [31:0] addr=32'h00400000,din=0;
    reg oe=1,we=0;
    reg [3:0] bw=15;
    wire [31:0] ma,md,dout,idata,ddata;
    wire io,doe,dwe,fault;
    wire [3:0] dbw;
    address_decoder #(.IMEM_WORDS(8),.DMEM_WORDS(8)) ad(addr,din,oe,we,bw,idata,ddata,ma,md,dout,io,doe,dwe,dbw,fault);
    // ma/md são encaminhados às memórias; io/doe/dwe habilitam somente o destino selecionado.
    imem #(.WORDS(8),.INIT_FILE("tb/data/fetch.hex")) im(ma,io,idata);
    dmem #(.WORDS(8)) dm(clk,ma,doe,dwe,dbw,md,ddata);
    initial begin
        // Primeiro lê a ROM; depois escreve/lê uma palavra na RAM pelo mesmo barramento.
        #1; if(dout!==32'h00100093||fault) $fatal(1,"instruction read");
        @(negedge clk); addr=32'h10010000; oe=0; we=1; din=32'hf4f3f2f1;
        @(posedge clk); #1;
        @(negedge clk); we=0; oe=1;
        @(posedge clk); #1; if(dout!==32'hf4f3f2f1||fault) $fatal(1,"data read");
        @(negedge clk); we=1; oe=0; bw=4; din=32'h00120000;
        // Máscara 0100 atualiza somente o terceiro byte, preservando os demais.
        @(posedge clk); #1;
        @(negedge clk); we=0; oe=1;
        @(posedge clk); #1; if(dout!==32'hf412f2f1) $fatal(1,"partial bus write");
        @(negedge clk); addr=32'h00400000; we=1; oe=0;
        // Escrita na ROM deve gerar fault; releitura confirma que o conteúdo não mudou.
        #1; if(!fault||dwe||io) $fatal(1,"ROM write protection");
        @(posedge clk); #1;
        @(negedge clk); we=0; oe=1; #1;
        if(dout!==32'h00100093) $fatal(1,"ROM corrupted");
        $display("PASS memory_bus: ROM/RAM routing, byte writes and ROM protection"); $finish;
    end
endmodule
