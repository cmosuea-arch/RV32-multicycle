`timescale 1ns/1ps
module tb_simple_system;
    reg clk=0; always #5 clk=~clk;
    reg rst=1;
    wire done,success,fault;
    integer cycles,i,checks=0;
    simple_system dut(clk,rst,done,success,fault);
    task reset_system;
        begin
            @(negedge clk); rst=1;
            @(posedge clk); #1;
            if(done || success || fault) $fatal(1,"simple reset failed");
        end
    endtask
    task run_to_done(input reg expected_success);
        begin
            @(negedge clk); rst=0;
            begin : waiting
                for(cycles=0;cycles<10000;cycles=cycles+1) begin
                    @(posedge clk); #1;
                    if(fault) $fatal(1,"simple fault pc=%h",dut.address);
                    if(done) begin
                        if(success!==expected_success) $fatal(1,"simple signature failed: %h",dut.data_memory.mem[252]);
                        if(expected_success && dut.data_memory.mem[252]!==32'h600dc0de)
                            $fatal(1,"simple signature not written to RAM");
                        repeat(12) begin
                            @(posedge clk); #1;
                            if(!done || success!==expected_success || fault) $fatal(1,"simple unstable result");
                        end
                        checks=checks+1;
                        disable waiting;
                    end
                end
                $fatal(1,"simple timeout");
            end
        end
    endtask
    initial begin
        reset_system();
        // RAM começa sem conteúdo definido; startup deve preparar .data/.bss.
        run_to_done(1);
        reset_system(); run_to_done(1); // RAM suja do primeiro boot.
        reset_system();
        dut.data_memory.mem[252]=32'habcdef01;
        @(negedge clk); rst=0;
        begin : cancel_signature
            for(i=0;i<10000;i=i+1) begin
                @(negedge clk);
                if(dut.dmem_we && dut.mem_address==32'h100103f0) begin
                    rst=1; @(posedge clk); #1;
                    if(done || success || dut.data_memory.mem[252]!==32'habcdef01)
                        $fatal(1,"reset did not cancel signature store");
                    checks=checks+1;
                    disable cancel_signature;
                end
            end
            $fatal(1,"missing signature before reset");
        end
        run_to_done(1);
        // Programa de teste: SB no endereço de assinatura não termina; SW ruim termina com falha.
        reset_system();
        dut.instruction_memory.mem[0]=32'h100102b7; // lui t0,0x10010
        dut.instruction_memory.mem[1]=32'h3f028293; // addi t0,t0,0x3f0
        dut.instruction_memory.mem[2]=32'h00028023; // sb x0,0(t0)
        dut.instruction_memory.mem[3]=32'h0002a023; // sw x0,0(t0)
        dut.instruction_memory.mem[4]=32'h0000006f; // jal x0,0
        @(negedge clk); rst=0;
        repeat(12) begin @(posedge clk); #1; if(done || fault) $fatal(1,"partial store terminated system"); end
        run_to_done(0);
        reset_system();
        dut.instruction_memory.mem[0]=32'hffffffff;
        @(negedge clk); rst=0;
        repeat(8) begin @(posedge clk); #1; end
        if(!fault || done || success) $fatal(1,"illegal instruction did not report fault");
        checks=checks+1;
        reset_system();
        $readmemh("build/simple.hex",dut.instruction_memory.mem);
        run_to_done(1);
        $display("PASS simple_system: %0d boot/reset/signature/fault checks, provisional CRC firmware",checks);
        $finish;
    end
endmodule
