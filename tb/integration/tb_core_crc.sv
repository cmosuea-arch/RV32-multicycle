`timescale 1ns/1ps
module tb_core_crc;
    reg clk=0; always #5 clk=~clk;
    reg rst=1;
    wire fault,valid;
    wire [31:0] cpc,ci,cd;
    wire [4:0] rd;
    reg [31:0] epc,ei,ed;
    reg [4:0] erd;
    integer fd,status,n,cycles,crc_count;
    riscv_top #(.IMEM_WORDS(65536),.IMEM_FILE("build/crc.hex"),.EXPERIMENTAL_XICRC(1))
        dut(clk,rst,fault,valid,cpc,ci,cd,rd);
    initial begin
        fd=$fopen("build/crc.trace","r");
        if(!fd) $fatal(1,"missing CRC trace");
        @(posedge clk); #1; @(negedge clk); rst=0;
        n=0; cycles=0; crc_count=0;
        while(!$feof(fd)) begin
            status=$fscanf(fd,"%h %h %h %h\n",epc,ei,erd,ed);
            if(status!=4) $fatal(1,"bad CRC trace");
            begin : await_commit
                forever begin
                    @(posedge clk); cycles=cycles+1;
                    if(fault || cycles>200000) $fatal(1,"CRC fault/timeout pc=%h",cpc);
                    if(valid) begin
                        if({cpc,ci,rd,cd}!=={epc,ei,erd,ed})
                            $fatal(1,"CRC trace #%0d pc=%h data=%h expected=%h",n,cpc,cd,ed);
                        if(ci[6:0]==7'h33 && ci[31:25]==7'h40) crc_count=crc_count+1;
                        #1;
                        if(erd!=0 && dut.core.register_file.regs[erd]!==ed) $fatal(1,"CRC RF mismatch");
                        disable await_commit;
                    end
                    #1;
                end
            end
            n=n+1;
        end
        if(crc_count!=2127) $fatal(1,"incomplete CRC trace: %0d",crc_count);
        if(dut.data_memory.mem[0]!==32'h29b1 || dut.data_memory.mem[1]!==32'h29b1)
            $fatal(1,"CRC stream packing/store failed");
        // Reset após uso da extensão limpa estado arquitetural e reinicia o fetch.
        @(negedge clk); rst=1; @(posedge clk); #1;
        if(valid || fault || dut.core.register_file.regs[1]!==0 || dut.core.current_pc!==32'h00400000)
            $fatal(1,"CRC reset failed");
        $display("PASS core_crc: %0d retirements, %0d CRC, overlap/x0/stream/store/reset",n,crc_count);
        $finish;
    end
endmodule
