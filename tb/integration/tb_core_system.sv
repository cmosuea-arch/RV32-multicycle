`timescale 1ns/1ps
module tb_core_system;
    // Executa store/FENCE/load e termina por ECALL ou EBREAK, observando a EEI.
    reg clk=0; always #5 clk=~clk;
    reg rst=1;
    wire fault,valid,trap,ebreak;
    wire [31:0] cpc,ci,cd,trap_pc;
    wire [4:0] rd;
    integer i,j,k,kind,cycles,retired,writes,fences=0,ecalls=0,ebreaks=0;
    reg [31:0] fence_word,trap_word,expected_value;
    reg [4:0] expected_rd;
    riscv_top #(.IMEM_WORDS(32),.DMEM_WORDS(16)) dut(
        clk,rst,fault,valid,cpc,ci,cd,rd,trap,ebreak,trap_pc);

    task reset_core;
        // Reset limpa apenas estado/RF, cancela pedidos e permite nova execução.
        begin
            @(negedge clk); rst=1;
            #1;
            if(trap || valid || dut.we || dut.oe) $fatal(1,"reset did not suppress outputs");
            @(posedge clk); #1;
            if(fault || trap || ebreak || trap_pc!==0 || dut.core.current_pc!==32'h00400000)
                $fatal(1,"reset failed to recover terminal state");
        end
    endtask

    task prepare(input [31:0] requested_trap,input [31:0] fence);
        begin
            for(j=0;j<32;j=j+1) dut.instruction_memory.mem[j]=32'hffffffff;
            dut.instruction_memory.mem[0]=32'h100100b7; // lui x1,0x10010
            dut.instruction_memory.mem[1]=32'h5a500113; // addi x2,x0,0x5a5
            dut.instruction_memory.mem[2]=32'h0020a023; // sw x2,0(x1)
            dut.instruction_memory.mem[3]=fence;
            dut.instruction_memory.mem[4]=32'h0000a183; // lw x3,0(x1)
            dut.instruction_memory.mem[5]=32'h00118213; // addi x4,x3,1
            dut.instruction_memory.mem[6]=requested_trap;
            dut.instruction_memory.mem[7]=32'h0000a023; // store posterior proibido
            dut.instruction_memory.mem[8]=32'h00000193; // escrita RF posterior proibida
            dut.data_memory.mem[0]=32'hdeadbeef;
        end
    endtask

    task run_to_trap(input reg expected_ebreak);
        begin
            retired=0; writes=0;
            @(negedge clk); rst=0;
            begin : waiting
                for(cycles=0;cycles<80;cycles=cycles+1) begin
                    @(posedge clk);
                    if(fault) $fatal(1,"legal system instruction entered FAULT");
                    if(dut.dmem_we) writes=writes+1;
                    if(valid) begin
                        if(retired>=6 || cpc!==32'h00400000+4*retired ||
                           ci!==dut.instruction_memory.mem[retired])
                            $fatal(1,"trap retired or incorrect PC/order");
                        case(retired)
                            0: begin expected_rd=1; expected_value=32'h10010000; end
                            1: begin expected_rd=2; expected_value=32'h5a5; end
                            4: begin expected_rd=3; expected_value=32'h5a5; end
                            5: begin expected_rd=4; expected_value=32'h5a6; end
                            default: begin expected_rd=0; expected_value=0; end
                        endcase
                        if(rd!==expected_rd || cd!==expected_value)
                            $fatal(1,"wrong commit effects at instruction %0d",retired);
                        if(retired==3) begin
                            if(writes!=1 || dut.data_memory.mem[0]!==32'h5a5 || dut.we || dut.oe)
                                $fatal(1,"FENCE ordering or side effects");
                            fences=fences+1;
                        end
                        retired=retired+1;
                    end
                    #1;
                    if(trap) begin
                        if(retired!=6 || writes!=1 || ebreak!==expected_ebreak ||
                           trap_pc!==32'h00400018 || cpc!==trap_pc ||
                           ci!==dut.instruction_memory.mem[6])
                            $fatal(1,"imprecise trap or wrong reason");
                        // Todos os registradores, inclusive rd arbitrário de FENCE, ficam intactos.
                        if(dut.core.a!==0) $fatal(1,"x0 changed");
                        for(k=1;k<32;k=k+1) begin
                            case(k)
                                1: expected_value=32'h10010000;
                                2,3: expected_value=32'h5a5;
                                4: expected_value=32'h5a6;
                                default: expected_value=0;
                            endcase
                            if(dut.core.register_file.regs[k]!==expected_value)
                                $fatal(1,"trap/FENCE changed register x%0d",k);
                        end
                        repeat(6) begin
                            @(posedge clk); #1;
                            if(!trap || fault || valid || dut.we || dut.oe ||
                               trap_pc!==32'h00400018 || ebreak!==expected_ebreak ||
                               dut.data_memory.mem[0]!==32'h5a5)
                                $fatal(1,"trap not terminal or subsequent access executed");
                        end
                        if(expected_ebreak) ebreaks=ebreaks+1; else ecalls=ecalls+1;
                        disable waiting;
                    end
                end
                $fatal(1,"system trap timeout");
            end
        end
    endtask

    initial begin
        // Cobre 256 máscaras pred/succ, modos fm e campos rs1/rd não nulos.
        for(kind=0;kind<2;kind=kind+1) begin
            trap_word=kind==0?32'h00000073:32'h00100073;
            for(i=0;i<256;i=i+1) begin
                reset_core();
                fence_word=((i&15)<<28)|(i<<20)|((i&31)<<15)|(((i>>3)&31)<<7)|32'h0f;
                prepare(trap_word,fence_word);
                run_to_trap(kind==1);
            end
        end
        // Reset antes da borda de entrada em TRAP cancela o pedido.
        reset_core(); prepare(32'h00000073,32'h0ff0000f);
        @(negedge clk); rst=0;
        begin : before_trap
            for(i=0;i<80;i=i+1) begin
                @(negedge clk);
                if(dut.core.state==2 && dut.core.instruction==32'h00000073) begin
                    rst=1; @(posedge clk); #1;
                    if(trap || valid || fault || dut.core.current_pc!==32'h00400000)
                        $fatal(1,"reset did not cancel pending trap");
                    disable before_trap;
                end
            end
            $fatal(1,"missing pending trap");
        end
        // Recuperação executa código normal depois dos dois tipos de trap.
        reset_core();
        dut.instruction_memory.mem[0]=32'h00700293; // addi x5,x0,7
        dut.instruction_memory.mem[1]=32'h0000006f; // jal x0,0
        @(negedge clk); rst=0;
        repeat(12) begin @(posedge clk); #1; if(trap || fault) $fatal(1,"reset recovery failed"); end
        if(dut.core.register_file.regs[5]!==7) $fatal(1,"no forward progress after reset");
        $display("PASS core_system: FENCE=%0d ECALL=%0d EBREAK=%0d, precise terminal traps, no retirement/side effects, reset recovery",fences,ecalls,ebreaks);
        $finish;
    end
endmodule
