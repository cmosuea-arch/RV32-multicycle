`timescale 1ns/1ps
// Experimento CMOS: capacidades fixas e programa embutido na ROM durante a síntese.
// Top reduzido: ROM de 2 KiB, RAM de 1 KiB e saídas para indicar término do firmware.
module simple_system #(
    parameter ROM_FILE="build/simple.hex"
)(
    input logic clk_i,rst_i,
    output reg done_o,success_o,
    output wire fault_o
);
    wire [31:0] address,wdata,rdata,mem_address,mem_data,idata,ddata;
    wire oe,we,bus_fault,imem_oe,dmem_oe,dmem_we;
    wire [3:0] bw,dmem_bw;
    wire commit_valid,core_fault,core_trap,trap_ebreak;
    wire [31:0] trap_pc;
    wire [31:0] commit_pc,commit_instr,commit_data;
    wire [4:0] commit_rd;
    // Usa o mesmo contrato Xicrc do top de validação, com firmware próprio reduzido.
    riscv_core #(.EXPERIMENTAL_XICRC(1)) core(
        clk_i,rst_i,rdata,bus_fault,address,wdata,oe,we,bw,
        core_fault,commit_valid,commit_pc,commit_instr,commit_data,commit_rd,
        core_trap,trap_ebreak,trap_pc);
    // Interface reduzida sinaliza também o encerramento por trap, sem indicar sucesso.
    assign fault_o=core_fault || core_trap;
    address_decoder #(.IMEM_WORDS(512),.DMEM_WORDS(256)) bus_decoder(
        address,wdata,oe,we,bw,idata,ddata,mem_address,mem_data,rdata,
        imem_oe,dmem_oe,dmem_we,dmem_bw,bus_fault);
    imem #(.WORDS(512),.INIT_FILE(ROM_FILE)) instruction_memory(mem_address,imem_oe,idata);
    dmem #(.WORDS(256)) data_memory(clk_i,mem_address,dmem_oe,dmem_we,dmem_bw,mem_data,ddata);
    // Observa uma escrita real na RAM; byte/halfword não encerram o programa.
    // A primeira word na assinatura fixa done; success indica o valor esperado.
    // Ambos retêm o resultado até reset; o firmware pode continuar no loop final.
    always @(posedge clk_i) begin
        if(rst_i) begin done_o<=0; success_o<=0; end
        else if(!done_o && dmem_we && mem_address==32'h100103f0 && dmem_bw==4'hf) begin
            done_o<=1;
            success_o<=mem_data==32'h600dc0de;
        end
    end
endmodule
