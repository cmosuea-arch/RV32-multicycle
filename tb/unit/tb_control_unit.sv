`timescale 1ns/1ps
module tb_control_unit;
    // Confere a ordem da FSM: FETCH=0, DECODE=1, EXECUTE=2, WRITEBACK=3, MEMORY=4, FAULT=5.
    // Clock de 10 ns; entradas mudam na descida, estado é conferido após a subida.
    reg clk=0; always #5 clk=~clk;
    reg rst=1,illegal=0,load=0,store_op=0,fault=0,trap_request=0;
    wire [2:0] state;
    control_unit dut(clk,rst,illegal,load,store_op,fault,state,trap_request);
    task next_state(input [2:0] expected);
        // Espera uma transição e compara o estado já atualizado pelo RTL.
        begin @(posedge clk); #1; if(state!==expected) $fatal(1,"FSM got=%0d expected=%0d",state,expected); end
    endtask
    initial begin
        next_state(0); @(negedge clk); rst=0;
        // Instrução comum usa quatro estados; load/store acrescentam MEMORY.
        next_state(1); next_state(2); next_state(3); next_state(0);
        @(negedge clk); load=1;
        next_state(1); next_state(2); next_state(4); next_state(3); next_state(0);
        @(negedge clk); load=0; store_op=1;
        next_state(1); next_state(2); next_state(4); next_state(3); next_state(0);
        @(negedge clk); store_op=0;
        next_state(1); @(negedge clk); illegal=1;
        // Instrução ilegal entra em FAULT e permanece lá mesmo após retirar illegal.
        next_state(5); @(negedge clk); illegal=0; next_state(5);
        @(negedge clk); rst=1; next_state(0);
        // Reset recupera FETCH; uma falha externa volta a colocar a FSM em FAULT.
        @(negedge clk); rst=0; fault=1; next_state(5);
        // Trap solicitado em EXECUTE não passa por WRITEBACK e só sai por reset.
        @(negedge clk); rst=1; fault=0; next_state(0);
        @(negedge clk); rst=0; trap_request=1;
        next_state(1); next_state(2); next_state(6);
        @(negedge clk); trap_request=0; fault=1; next_state(6); next_state(6);
        @(negedge clk); rst=1; next_state(0);
        @(negedge clk); rst=0; fault=0; trap_request=1; illegal=1;
        next_state(1); next_state(5); // Ilegal não se transforma em trap solicitado.
        $display("PASS control_unit: stages, memory, illegal, fault, terminal TRAP and reset priority"); $finish;
    end
endmodule
