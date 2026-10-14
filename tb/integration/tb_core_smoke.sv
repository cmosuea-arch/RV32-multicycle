`timescale 1ns/1ps
module tb_core_smoke;
    // Executa cinco instruções no core completo e confere cada aposentadoria (commit).
    reg clk=0; always #5 clk=~clk;
    reg rst=1;
    reg [31:0] rom[0:4];
    wire [31:0] address,data,wdata,commit_pc,commit_instr,commit_data;
    wire oe,we,fault,valid;
    wire [3:0] bw;
    wire [4:0] rd;
    integer n,cycles;
    reg [31:0] expected[0:4];
    assign data=oe&&address>=32'h00400000&&address<32'h00400014 ? rom[(address-32'h00400000)>>2] : 0;
    // ROM local responde ao fetch; esta bancada não precisa de RAM nem de stores.
    riscv_core dut(clk,rst,data,1'b0,address,wdata,oe,we,bw,fault,valid,commit_pc,commit_instr,commit_data,rd);
    initial begin
        // Programa e resultados esperados incluem dependências entre registradores e escrita em x0.
        rom[0]=32'h00500093; expected[0]=5; // addi x1,x0,5
        rom[1]=32'hffd00113; expected[1]=32'hfffffffd; // addi x2,x0,-3
        rom[2]=32'h002081b3; expected[2]=2; // add x3,x1,x2
        rom[3]=32'h40208233; expected[3]=8; // sub x4,x1,x2
        rom[4]=32'h00100013; expected[4]=0; // addi x0,x0,1
        @(posedge clk); #1; @(negedge clk); rst=0;
        n=0;
        for(cycles=0;cycles<100;cycles=cycles+1) begin
            // Limite de ciclos detecta travamento; valid indica instrução concluída pelo core.
            @(posedge clk);
            if(fault || we) $fatal(1,"smoke fault/store");
            if(valid) begin
                // Confere PC, palavra executada, destino e dado de cada instrução, na ordem.
                if(commit_pc!==(32'h00400000+4*n)||commit_instr!==rom[n]||commit_data!==expected[n])
                    $fatal(1,"smoke retirement %0d got=%h expected=%h",n,commit_data,expected[n]);
                if((n<4 && rd!==(n+1))||(n==4 && rd!==0)) $fatal(1,"smoke rd");
                n=n+1;
                if(n==5) begin
                    // #1 espera a escrita no RF e confirma o estado real além dos sinais commit.
                    #1;
                    if(dut.register_file.regs[4]!==8) $fatal(1,"physical RF writeback");
                    $display("PASS core_smoke: ADD SUB ADDI, dependencies and x0 through FSM"); $finish;
                end
            end
            #1;
        end
        $fatal(1,"smoke timeout");
    end
endmodule
