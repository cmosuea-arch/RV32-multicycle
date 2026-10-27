`timescale 1ns/1ps
module tb_isa;
    // Executa o programa ISA e compara cada instrução com o trace arquitetural do Python.
    // O trace cobre 45 tipos que aposentam; os traps são conferidos em tb_core_system.
    reg clk=0; always #5 clk=~clk;
    wire trap,trap_ebreak;
    wire [31:0] trap_pc;
    reg rst=1;
    wire [31:0] address,data,wdata,commit_pc,commit_instr,commit_data;
    wire oe,we,fault,valid;
    wire [3:0] bw;
    wire [4:0] rd;
    reg [31:0] expected_pc,expected_instr,expected_data;
    reg [4:0] expected_rd;
    integer fd,status,n,cycles,mfd,checked_bytes,stores=0,physical_writes=0;
    reg [31:0] expected_address;
    reg [7:0] expected_byte;
    riscv_top #(.IMEM_WORDS(131072),.IMEM_FILE("build/isa.hex")) dut(clk,rst,fault,valid,commit_pc,commit_instr,commit_data,rd,trap,trap_ebreak,trap_pc);
    assign address=dut.address;
    always @(posedge clk) if(!rst&&dut.dmem_we) physical_writes=physical_writes+1;
    // Conta stores físicos para detectar escritas ausentes ou repetidas entre estados da FSM.
    initial begin
        fd=$fopen("build/isa.trace","r");
        if(!fd) $fatal(1,"missing trace");
        @(posedge clk); #1; @(negedge clk); rst=0; n=0; cycles=0;
        while(!$feof(fd)) begin
            // Uma linha esperada contém PC, instrução, rd e dado; ela aguarda o próximo commit.
            status=$fscanf(fd,"%h %h %h %h\n",expected_pc,expected_instr,expected_rd,expected_data);
            if(status!=4) $fatal(1,"bad trace");
            begin : await_commit
                // Bloco nomeado permite sair com disable quando a instrução esperada termina.
                forever begin
                    @(posedge clk); cycles=cycles+1;
                    if(fault || trap) $fatal(1,"ISA fault at pc=%h instruction=%h",address,commit_instr);
                    if(cycles>1000000) $fatal(1,"ISA timeout");
                    if(valid) begin
                        // Compara efeitos arquiteturais antes da borda concluir a escrita no RF.
                        if(commit_instr[6:0]==7'h23) stores=stores+1;
                        if(commit_pc!==expected_pc||commit_instr!==expected_instr||rd!==expected_rd||commit_data!==expected_data)
                            $fatal(1,"ISA #%0d pc=%h instr=%h rd=%0d got=%h expected PC=%h ins=%h rd=%0d data=%h",n,commit_pc,commit_instr,rd,commit_data,expected_pc,expected_instr,expected_rd,expected_data);
                        #1;
                        // Depois da atualização registrada, verifica também o valor armazenado no RF.
                        if(rd!=0 && dut.core.register_file.regs[expected_rd]!==expected_data) $fatal(1,"RF mismatch");
                        disable await_commit;
                    end
                    #1;
                end
            end
            n=n+1;
        end
        if(n==0) $fatal(1,"empty trace");
        if(stores!=physical_writes) $fatal(1,"store count: retired=%0d writes=%0d",stores,physical_writes);
        // Ao terminar o trace, compara byte a byte o conteúdo final previsto para a RAM.
        mfd=$fopen("build/isa_memory.vec","r"); checked_bytes=0;
        if(!mfd) $fatal(1,"missing expected memory");
        while(!$feof(mfd)) begin
            status=$fscanf(mfd,"%h %h\n",expected_address,expected_byte);
            if(status!=2) $fatal(1,"bad memory vector");
            if(dut.data_memory.mem[(expected_address-32'h10010000)>>2][8*expected_address[1:0]+:8]!==expected_byte)
                $fatal(1,"memory mismatch address=%h",expected_address);
            checked_bytes=checked_bytes+1;
        end
        $display("PASS isa: %0d retirements, %0d stores and %0d final bytes match Python",n,stores,checked_bytes); $finish;
    end
endmodule
