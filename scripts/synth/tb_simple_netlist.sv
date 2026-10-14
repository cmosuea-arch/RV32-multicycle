`timescale 1ns/1ps
// Apenas pinos: usa a netlist genérica do Yosys, sem acesso à ROM/RAM internas.
module tb_simple_netlist;
    reg clk=0; always #5 clk=~clk;
    reg rst=1;
    wire done,success,fault;
    integer boot,cycles;
    simple_system dut(.clk_i(clk),.rst_i(rst),.done_o(done),.success_o(success),.fault_o(fault));
    initial begin
        for(boot=0;boot<2;boot=boot+1) begin
            @(negedge clk); rst=1;
            @(posedge clk); #1;
            if(done || success || fault) $fatal(1,"netlist reset failed");
            @(negedge clk); rst=0;
            begin : waiting
                for(cycles=0;cycles<10000;cycles=cycles+1) begin
                    @(posedge clk); #1;
                    if(fault) $fatal(1,"netlist fault");
                    if(done) begin
                        if(success!==1) $fatal(1,"netlist firmware failed");
                        disable waiting;
                    end
                end
                $fatal(1,"netlist timeout");
            end
        end
        $display("PASS simple_netlist: two boots with ROM constants and uninitialized RAM");
        $finish;
    end
endmodule
