`timescale 1ns/1ps
// Integration top. Physical UART/GPIO pin contract remains unspecified.
// Integra core, decodificador de endereços, ROM e RAM com capacidades parametrizáveis.
module riscv_top #(
    parameter integer IMEM_WORDS=1048576,DMEM_WORDS=2048,
    parameter IMEM_FILE="",
    parameter bit EXPERIMENTAL_XICRC=0
)(input logic clk_i,rst_i,
  output wire fault_o,commit_valid_o,
  output wire [31:0] commit_pc_o,commit_instr_o,commit_data_o,
  output wire [4:0] commit_rd_o);
    wire [31:0] address,wdata,rdata,mem_address,mem_data,idata,ddata;
    wire oe,we,bus_fault,imem_oe,dmem_oe,dmem_we;
    wire [3:0] bw,dmem_bw;
    // O core pede acessos; rdata e bus_fault retornam pelo decodificador do barramento.
    riscv_core #(.EXPERIMENTAL_XICRC(EXPERIMENTAL_XICRC)) core(clk_i,rst_i,rdata,bus_fault,address,wdata,oe,we,bw,
                    fault_o,commit_valid_o,commit_pc_o,commit_instr_o,commit_data_o,commit_rd_o);
    address_decoder #(.IMEM_WORDS(IMEM_WORDS),.DMEM_WORDS(DMEM_WORDS)) bus_decoder(
        address,wdata,oe,we,bw,idata,ddata,mem_address,mem_data,rdata,imem_oe,dmem_oe,dmem_we,dmem_bw,bus_fault);
    // IMEM responde combinacionalmente; DMEM usa o clock para leitura/escrita.
    imem #(.WORDS(IMEM_WORDS),.INIT_FILE(IMEM_FILE)) instruction_memory(mem_address,imem_oe,idata);
    dmem #(.WORDS(DMEM_WORDS)) data_memory(clk_i,mem_address,dmem_oe,dmem_we,dmem_bw,mem_data,ddata);
endmodule
