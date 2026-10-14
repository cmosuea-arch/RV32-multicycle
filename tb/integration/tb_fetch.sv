`timescale 1ns/1ps
module tb_fetch;
    // Integra PC -> ROM -> IR -> imediato; usa as oito palavras de tb/data/fetch.hex.
    reg clk=0; always #5 clk=~clk;
    reg rst=1,enable=0;
    wire [31:0] address,plus4,data,instruction,imm;
    integer i;
    pc p(clk,rst,enable,plus4,address,plus4);
    // O mesmo enable avança o PC, permite leitura da ROM e captura a instrução no IR.
    imem #(.WORDS(8),.INIT_FILE("tb/data/fetch.hex")) m(address,enable,data);
    ir r(clk,rst,enable,data,instruction);
    imm_ext x(instruction,imm);
    initial begin
        @(posedge clk); #1;
        @(negedge clk); rst=0; enable=1;
        for(i=0;i<8;i=i+1) begin
            // Antes da subida verifica o endereço; depois confere instrução capturada e imediato.
            if(address !== (32'h00400000+4*i)) $fatal(1,"fetch PC %0d",i);
            @(posedge clk); #1;
            if(instruction !== (32'h00100093+(i<<20)) || imm!==(i+1)) $fatal(1,"fetch IR %0d",i);
            @(negedge clk);
        end
        enable=0;
        // Desabilitar a busca deve reter a última instrução, ADDI x1,x0,8.
        @(posedge clk); #1;
        if(instruction!==32'h00800093) $fatal(1,"fetch hold");
        $display("PASS fetch: PC BASE..BASE+28, ROM, IR and immediate"); $finish;
    end
endmodule
