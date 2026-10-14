`timescale 1ns/1ps
module imem #(
    parameter integer WORDS=1048576,
    parameter [31:0] BASE=32'h00400000,
    parameter INIT_FILE=""
)(input logic [31:0] address_i,input logic oe_i,output wire [31:0] data_o);
    localparam integer IW=(WORDS>1)?$clog2(WORDS):1;
    reg [31:0] mem [0:WORDS-1];
    wire [31:0] index=(address_i-BASE)>>2;
    integer i;
    initial begin
        // Fontes de inicialização exclusivas: evita zeros sobrepondo a ROM na síntese.
        // Quando há arquivo, ele deve conter WORDS palavras (geradores fazem padding).
        if(INIT_FILE!="") $readmemh(INIT_FILE,mem);
        else for(i=0;i<WORDS;i=i+1) mem[i]=0;
    end
    assign data_o=(oe_i && address_i>=BASE && index<WORDS && address_i[1:0]==0)
                 ? mem[index[IW-1:0]] : 32'b0;
endmodule
