`timescale 1ns/1ps
// RAM de dados: leitura e escrita ocorrem na borda de subida do clock.
module dmem #(
    parameter integer WORDS=2048,
    parameter [31:0] BASE=32'h10010000
)(input logic clk_i,input logic [31:0] address_i,
  input logic oe_i,we_i,input logic [3:0] bw_i,input logic [31:0] data_i,
  output reg [31:0] data_o);
    localparam integer IW=(WORDS>1)?$clog2(WORDS):1;
    reg [31:0] mem[0:WORDS-1];
    // Converte endereço absoluto em índice local e rejeita palavras fora da RAM.
    wire [31:0] index=(address_i-BASE)>>2;
    wire valid=address_i>=BASE&&index<WORDS&&address_i[1:0]==0;
    integer lane;
    // Sem oe, data_o retém a leitura anterior. A RAM não é apagada por reset.
    // Se ler e escrever a mesma palavra na mesma borda, a leitura vê o valor anterior.
    // O startup do firmware prepara .data/.bss; não presumir zero no primeiro boot.
    always @(posedge clk_i) begin
        if(oe_i) data_o<=valid?mem[index[IW-1:0]]:32'b0;
        if(we_i&&valid)
            // Cada bit de bw altera um byte; os outros bytes preservam seu valor.
            for(lane=0;lane<4;lane=lane+1)
                if(bw_i[lane]) mem[index[IW-1:0]][lane*8+:8]<=data_i[lane*8+:8];
    end
endmodule
