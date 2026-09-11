`timescale 1ns/1ps
module tb_control_unit;
    reg clk=0; always #5 clk=~clk;
    reg rst=1,illegal=0,load=0,store_op=0,fault=0;
    wire [2:0] state;
    control_unit dut(clk,rst,illegal,load,store_op,fault,state);
    task next_state(input [2:0] expected);
        begin @(posedge clk); #1; if(state!==expected) $fatal(1,"FSM got=%0d expected=%0d",state,expected); end
    endtask
    initial begin
        next_state(0); @(negedge clk); rst=0;
        next_state(1); next_state(2); next_state(3); next_state(0);
        @(negedge clk); load=1;
        next_state(1); next_state(2); next_state(4); next_state(3); next_state(0);
        @(negedge clk); load=0; store_op=1;
        next_state(1); next_state(2); next_state(4); next_state(3); next_state(0);
        @(negedge clk); store_op=0;
        next_state(1); @(negedge clk); illegal=1;
        next_state(5); @(negedge clk); illegal=0; next_state(5);
        @(negedge clk); rst=1; next_state(0);
        @(negedge clk); rst=0; fault=1; next_state(5);
        $display("PASS control_unit: four stages, illegal, fault and reset"); $finish;
    end
endmodule
