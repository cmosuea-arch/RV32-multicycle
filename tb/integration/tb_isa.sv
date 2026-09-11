`timescale 1ns/1ps
module tb_isa;
    reg clk=0; always #5 clk=~clk;
    reg rst=1;
    wire [31:0] address,data,wdata,commit_pc,commit_instr,commit_data;
    wire oe,we,fault,valid;
    wire [3:0] bw;
    wire [4:0] rd;
    reg [31:0] expected_pc,expected_instr,expected_data;
    reg [4:0] expected_rd;
    integer fd,status,n,cycles;
    imem #(.WORDS(65536),.INIT_FILE("build/isa.hex")) rom(address,oe,data);
    riscv_core dut(clk,rst,data,1'b0,address,wdata,oe,we,bw,fault,valid,commit_pc,commit_instr,commit_data,rd);
    initial begin
        fd=$fopen("build/isa.trace","r");
        if(!fd) $fatal(1,"missing trace");
        @(posedge clk); #1; @(negedge clk); rst=0; n=0; cycles=0;
        while(!$feof(fd)) begin
            status=$fscanf(fd,"%h %h %h %h\n",expected_pc,expected_instr,expected_rd,expected_data);
            if(status!=4) $fatal(1,"bad trace");
            begin : await_commit
                forever begin
                    @(posedge clk); cycles=cycles+1;
                    if(fault) $fatal(1,"ISA fault at pc=%h instruction=%h",address,commit_instr);
                    if(cycles>1000000) $fatal(1,"ISA timeout");
                    if(valid) begin
                        if(commit_pc!==expected_pc||commit_instr!==expected_instr||rd!==expected_rd||commit_data!==expected_data)
                            $fatal(1,"ISA #%0d pc=%h instr=%h rd=%0d got=%h expected PC=%h ins=%h rd=%0d data=%h",n,commit_pc,commit_instr,rd,commit_data,expected_pc,expected_instr,expected_rd,expected_data);
                        #1;
                        if(rd!=0 && dut.register_file.regs[expected_rd]!==expected_data) $fatal(1,"RF mismatch");
                        disable await_commit;
                    end
                    #1;
                end
            end
            n=n+1;
        end
        if(n==0) $fatal(1,"empty trace");
        $display("PASS isa: %0d retirements match Python architectural expectations",n); $finish;
    end
endmodule
