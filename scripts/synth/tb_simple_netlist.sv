`timescale 1ns/1ps
// Apenas pinos: usa a netlist genérica do Yosys, sem acesso à ROM/RAM internas.
module tb_simple_netlist;
    // A mesma interface de pinos permite testar o circuito produzido pela síntese.
    reg clk=0; always #5 clk=~clk;
    reg rst=1;
    wire done,success,fault;
    integer boot,cycles;
    simple_system dut(.clk_i(clk),.rst_i(rst),.done_o(done),.success_o(success),.fault_o(fault));
    initial begin
        // Executa dois boots; o segundo verifica reinicialização por software da RAM já usada.
        for(boot=0;boot<2;boot=boot+1) begin
            @(negedge clk); rst=1;
            @(posedge clk); #1;
            // #1 espera a atualização dos registradores; reset deve limpar as saídas observáveis.
            if(done || success || fault) $fatal(1,"netlist reset failed");
            @(negedge clk); rst=0;
            begin : waiting
                // Aguarda done com timeout, reprova fault e exige success=1 na assinatura final.
                for(cycles=0;cycles<10000;cycles=cycles+1) begin
                    @(posedge clk); #1;
                    if(fault) $fatal(1,"netlist fault");
                    if(done) begin
                        if(success!==1) $fatal(1,"netlist firmware failed");
                        disable waiting;
                        // Encerra só a espera deste boot, seguindo para o próximo reset.
                    end
                end
                $fatal(1,"netlist timeout");
            end
        end
        $display("PASS simple_netlist: two boots with ROM constants and uninitialized RAM");
        $finish;
    end
endmodule
