`timescale 1ns/1ps
module tb_memory_faults;
    // Testa falhas de memória no top integrado e verifica que nenhum dado é corrompido.
    reg clk=0; always #5 clk=~clk;
    reg rst=1;
    wire fault,valid;
    wire [31:0] cpc,ci,cd;
    wire [4:0] rd;
    integer i,cycles,retired,cases=0,writes=0;
    reg [31:0] operations[0:7];
    riscv_top #(.IMEM_WORDS(16),.DMEM_WORDS(4)) dut(clk,rst,fault,valid,cpc,ci,cd,rd);
    always @(posedge clk) if(!rst&&dut.dmem_we) writes=writes+1;
    // Conta escritas reais na RAM, separadamente das instruções concluídas.
    task prepare;
        // Monta programa-base: endereço RAM, dado 5a e um SW válido antes da operação defeituosa.
        begin
            @(negedge clk); rst=1;
            @(posedge clk); #1;
            for(i=0;i<16;i=i+1) dut.instruction_memory.mem[i]=0;
            dut.instruction_memory.mem[0]=32'h100100b7; // LUI x1,DMEM
            dut.instruction_memory.mem[1]=32'h05a00113; // ADDI x2,0,0x5a
            dut.instruction_memory.mem[2]=32'h0020a023; // SW x2,0(x1)
            retired=0; writes=0;
        end
    endtask
    task check_fault(input integer allowed);
        // Aguarda FAULT com timeout; aceita somente o store inicial e preserva seu conteúdo.
        begin
            @(negedge clk); rst=0;
            begin : waiting
                for(cycles=0;cycles<80;cycles=cycles+1) begin
                    @(posedge clk);
                    if(valid) retired=retired+1;
                    if(fault) begin
                        if(retired!=allowed||writes!=1||dut.data_memory.mem[0]!==32'h5a)
                            $fatal(1,"fault effects retired=%0d expected=%0d writes=%0d",retired,allowed,writes);
                        repeat(2) begin @(posedge clk); #1; if(valid||dut.we||dut.oe||!fault) $fatal(1,"fault activity"); end
                        cases=cases+1;
                        disable waiting;
                        // Encerra a espera do caso atual, permitindo testar a próxima falha.
                    end
                    #1;
                end
                $fatal(1,"memory fault timeout");
            end
        end
    endtask
    integer k;
    initial begin
        // Oito operações exercitam offsets desalinhados de LH/LW/SH/SW.
        operations[0]=32'h00109183; operations[1]=32'h0010a183;
        operations[2]=32'h0020a183; operations[3]=32'h0030a183;
        operations[4]=32'h002090a3; operations[5]=32'h0020a0a3;
        operations[6]=32'h0020a123; operations[7]=32'h0020a1a3;
        for(k=0;k<8;k=k+1) begin prepare(); dut.instruction_memory.mem[3]=operations[k]; check_fault(3); end
        prepare(); dut.instruction_memory.mem[3]=32'h00000237; dut.instruction_memory.mem[4]=32'h00022003; check_fault(4); // unmapped load x0
        // Casos seguintes cobrem escrita na ROM e acessos logo após o limite da RAM.
        prepare(); dut.instruction_memory.mem[3]=32'h00400237; dut.instruction_memory.mem[4]=32'h00222023; check_fault(4); // ROM store
        if(dut.instruction_memory.mem[0]!==32'h100100b7) $fatal(1,"ROM changed");
        prepare(); dut.instruction_memory.mem[3]=32'h0100a183; check_fault(3); // upper boundary load
        prepare(); dut.instruction_memory.mem[3]=32'h0020a823; check_fault(3); // upper boundary store
        // Reset during a pending STORE cancels the bus write and preserves RAM.
        prepare(); @(negedge clk); rst=0;
        wait(dut.core.state==4); @(negedge clk); rst=1; #1;
        if(dut.dmem_we) $fatal(1,"write while reset asserted");
        @(posedge clk); #1;
        if(writes!=0||dut.data_memory.mem[0]!==32'h5a) $fatal(1,"reset store cancellation");
        $display("PASS memory_faults: %0d misaligned/unmapped/ROM faults and reset cancellation",cases); $finish;
    end
endmodule
