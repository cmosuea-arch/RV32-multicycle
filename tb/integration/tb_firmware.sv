`timescale 1ns/1ps
module tb_firmware;
    reg clk=0; always #5 clk=~clk;
    reg rst=1;
    wire fault,valid;
    wire [31:0] cpc,ci,cd;
    wire [4:0] rd;
    integer cycles,n=0;
    riscv_top #(.IMEM_WORDS(4096),.IMEM_FILE("build/smoke.hex")) dut(clk,rst,fault,valid,cpc,ci,cd,rd);
    initial begin
        if($test$plusargs("WAVE")) begin
            $dumpfile("results/waveforms/smoke.vcd");
            $dumpvars(0,dut.core);
        end
        @(posedge clk); #1; @(negedge clk); rst=0;
        for(cycles=0;cycles<100000;cycles=cycles+1) begin
            @(posedge clk);
            if(fault) $fatal(1,"firmware fault pc=%h instr=%h",cpc,ci);
            if(valid) n=n+1;
            if(dut.dmem_we&&dut.mem_address==32'h10011ff0) begin
                if(dut.mem_data!==32'h600dc0de||dut.dmem_bw!==4'hf)
                    $fatal(1,"firmware failure signature=%h pc=%h",dut.mem_data,cpc);
                #1;
                if(dut.data_memory.mem[2044]!==32'h600dc0de) $fatal(1,"signature not stored");
                $display("PASS firmware: signature 600dc0de, %0d retirements, %0d cycles",n,cycles+1); $finish;
            end
            #1;
        end
        $fatal(1,"firmware timeout");
    end
endmodule
