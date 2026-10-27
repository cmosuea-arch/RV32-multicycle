`timescale 1ns/1ps
module tb_core_faults;
    // Injeta instruções inválidas, alvos desalinhados e falha de fetch no core baseline.
    reg clk=0; always #5 clk=~clk;
    reg rst=1,bus_error=0;
    reg [31:0] rom[0:15];
    wire [31:0] address,data,wdata,cpc,ci,cd;
    wire oe,we,fault,valid;
    wire [3:0] bw;
    wire [4:0] rd;
    integer i,cycles,retired,cases;
    assign data=oe&&address>=32'h00400000&&address<32'h00400040 ? rom[(address-32'h00400000)>>2] : 0;
    // Mantém a checagem explícita do perfil sem CRC, além das instruções inválidas.
    riscv_core #(.EXPERIMENTAL_XICRC(0)) dut(clk,rst,data,bus_error,address,wdata,oe,we,bw,fault,valid,cpc,ci,cd,rd);
    task clear_rom;
        // Reinicia o core, retira erro externo e limpa a ROM antes de montar cada caso.
        begin
            @(negedge clk); rst=1; bus_error=0;
            for(i=0;i<16;i=i+1) rom[i]=0;
            @(posedge clk); #1;
        end
    endtask
    task expect_fault(input integer allowed,input [31:0] expected_pc);
        // Espera FAULT, limitando ciclos e conferindo quantas instruções puderam concluir.
        begin
            @(negedge clk); rst=0; retired=0;
            begin : wait_fault
                for(cycles=0;cycles<80;cycles=cycles+1) begin
                    @(posedge clk);
                    if(valid) retired=retired+1;
                    if(we) $fatal(1,"unexpected memory write");
                    if(fault) begin
                        // Falha deve parar no PC esperado, sem store nem novas aposentadorias.
                        if(retired!=allowed||address!==expected_pc) $fatal(1,"fault side effects retired=%0d pc=%h",retired,address);
                        repeat(3) begin @(posedge clk); #1; if(!fault||valid||we||oe) $fatal(1,"fault not quiescent"); end
                        cases=cases+1;
                        disable wait_fault;
                        // disable sai apenas do bloco de espera; a bancada continua com o próximo caso.
                    end
                    #1;
                end
                $fatal(1,"fault timeout");
            end
        end
    endtask
    initial begin
        // Cada caso começa com reset e reaproveita expect_fault para checar efeitos colaterais.
        cases=0;
        clear_rom(); rom[0]=32'hffffffff; expect_fault(0,32'h00400000);
        clear_rom(); rom[0]=32'h802081b3; expect_fault(0,32'h00400000); // CRC disabled in baseline
        clear_rom(); rom[0]=32'h0220c1b3; expect_fault(0,32'h00400000); // DIV unsupported
        clear_rom(); rom[0]=32'h02009193; expect_fault(0,32'h00400000); // invalid shift
        clear_rom(); rom[0]=32'h00000073; expect_fault(0,32'h00400000);
        clear_rom(); rom[0]=32'h00100073; expect_fault(0,32'h00400000);
        clear_rom(); rom[0]=32'h0000000f; expect_fault(0,32'h00400000);
        clear_rom(); rom[0]=32'h00000163; expect_fault(0,32'h00400000); // taken misaligned
        clear_rom(); rom[0]=32'h00001163; expect_fault(1,32'h00400004); // untaken allowed
        clear_rom(); rom[0]=32'h002000ef; expect_fault(0,32'h00400000); // jal misaligned
        clear_rom(); rom[0]=32'h004000b7; rom[1]=32'h00208093; rom[2]=32'h000080e7;
        // JALR com alvo desalinhado não pode sobrescrever x1 com o endereço de retorno.
        expect_fault(2,32'h00400008);
        if(dut.register_file.regs[1]!==32'h00400002) $fatal(1,"fault wrote JALR link");
        clear_rom(); bus_error=1; rom[0]=32'h00100093; expect_fault(0,32'h00400000);
        $display("PASS core_faults: %0d invalid/control-flow faults, no side effects, reset recovery",cases); $finish;
    end
endmodule
