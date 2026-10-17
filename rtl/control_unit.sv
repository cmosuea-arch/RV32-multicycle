`timescale 1ns/1ps
// FSM multiciclo: fornece o estado usado pelo core para gerar os enables.
module control_unit(
    input logic clk_i,rst_i,illegal_i,load_i,store_i,fault_i,
    output reg [2:0] state_o
);
    localparam [2:0] FETCH=0,DECODE=1,EXECUTE=2,WRITEBACK=3,MEMORY=4,FAULT=5;
    // Reset síncrono ativo em 1 tem prioridade; FAULT só é abandonado por reset.
    always @(posedge clk_i) begin
        if(rst_i) state_o<=FETCH;
        else if(fault_i) state_o<=FAULT;
        else case(state_o)
            FETCH: state_o<=DECODE;
            // Decode valida a instrução antes de permitir sua execução.
            DECODE: if(illegal_i) state_o<=FAULT; else state_o<=EXECUTE;
            EXECUTE: if(load_i||store_i) state_o<=MEMORY; else state_o<=WRITEBACK;
            // Load/store usam uma borda extra para a DMEM síncrona.
            MEMORY: state_o<=WRITEBACK;
            WRITEBACK: state_o<=FETCH;
            default: state_o<=FAULT;
        endcase
    end
endmodule
