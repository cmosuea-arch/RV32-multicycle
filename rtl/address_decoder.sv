`timescale 1ns/1ps
// Interliga o barramento único do core às regiões de instruções e dados.
module address_decoder #(
    parameter integer IMEM_WORDS=1048576,DMEM_WORDS=2048,
    parameter [31:0] IMEM_BASE=32'h00400000,DMEM_BASE=32'h10010000
)(input logic [31:0] address_i,data_i,
  input logic oe_i,we_i,input logic [3:0] bw_i,
  input logic [31:0] imem_data_i,dmem_data_i,
  output wire [31:0] mem_address_o,mem_data_o,data_o,
  output wire imem_oe_o,dmem_oe_o,dmem_we_o,
  output wire [3:0] dmem_bw_o,output wire fault_o);
    // O endereço é em bytes; cada região contém WORDS palavras de quatro bytes.
    wire imem_hit=address_i>=IMEM_BASE&&((address_i-IMEM_BASE)>>2)<IMEM_WORDS;
    wire dmem_hit=address_i>=DMEM_BASE&&((address_i-DMEM_BASE)>>2)<DMEM_WORDS;
    // A LSU já seleciona o byte: as memórias recebem o endereço da palavra alinhada.
    assign mem_address_o={address_i[31:2],2'b0};
    assign mem_data_o=data_i;
    // oe habilita leitura; we e bw habilitam a escrita dos bytes da DMEM.
    assign imem_oe_o=oe_i&&imem_hit&&!we_i;
    assign dmem_oe_o=oe_i&&dmem_hit;
    assign dmem_we_o=we_i&&dmem_hit;
    assign dmem_bw_o=dmem_we_o?bw_i:4'b0;
    // O mux devolve a memória selecionada; escrita na ROM ou fora do mapa é falha.
    // Esta falha de acesso é distinta do trap solicitado por ECALL/EBREAK no core.
    assign data_o=imem_oe_o?imem_data_i:dmem_oe_o?dmem_data_i:32'b0;
    assign fault_o=(oe_i||we_i)&&(!(imem_hit||dmem_hit)||(we_i&&imem_hit));
endmodule
