`timescale 1ns/1ps
module tb_official_firmware;
    // Executa a imagem publicada e só aceita a escrita final de x4 seguida do loop.
    reg clk=0; always #5 clk=~clk;
    wire trap,trap_ebreak;
    wire [31:0] trap_pc;
    reg rst=1;
    wire fault,valid;
    wire [31:0] cpc,ci,cd;
    wire [4:0] rd;
    // build_official.py fornece ROM, tags de tipos e PCs/contagens esperados em meta.
    reg [31:0] expected_rom[0:511],meta[0:5];
    reg [5:0] tags[0:511];
    // A imagem oficial contém 44 tipos; FENCE/ECALL/EBREAK têm bancada própria.
    reg [43:0] seen=0;
    integer cycles,n=0,crc_count=0,loops=0,index;
    reg finished=0;
    riscv_top #(.IMEM_WORDS(512),.IMEM_FILE("build/official.hex"))
        dut(clk,rst,fault,valid,cpc,ci,cd,rd,trap,trap_ebreak,trap_pc);
    initial begin
        $readmemh("build/official.hex",expected_rom);
        $readmemh("build/official_tags.hex",tags);
        $readmemh("build/official_meta.hex",meta);
        if(meta[4]!==44 || meta[5]!==16) $fatal(1,"unexpected official inventory");
        if($test$plusargs("WAVE")) begin
            $dumpfile("results/waveforms/official.vcd");
            $dumpvars(0,dut.core);
        end
        @(posedge clk); #1; @(negedge clk); rst=0;
        for(cycles=1;cycles<=20000;cycles=cycles+1) begin
            @(posedge clk);
            if(fault || trap) $fatal(1,"official fault pc=%h instr=%h",cpc,ci);
            if(valid) begin
                n=n+1;
                if(cpc<32'h00400000 || cpc[1:0]!=0 ||
                   ((cpc-32'h00400000)>>2)>=meta[3])
                    $fatal(1,"official PC outside code: %h",cpc);
                index=(cpc-32'h00400000)>>2;
                if(ci!==expected_rom[index] || tags[index]==0 || tags[index]>44)
                    $fatal(1,"official fetch/tag mismatch pc=%h",cpc);
                seen[tags[index]-1]=1;
                if(ci[6:0]==7'h33 && ci[31:25]==7'h40) crc_count=crc_count+1;
                if(rd==4) begin
                    // Zero só aprova na escrita do PC final, nunca pela leitura de x4 no reset.
                    if(cpc==meta[2] || cd!==0) $fatal(1,"official FAIL x4=%h pc=%h",cd,cpc);
                    if(cpc!==meta[0] || ci!==32'h00000213 || finished)
                        $fatal(1,"unexpected official x4 write");
                    finished=1;
                end else if(finished) begin
                    if(cpc!==meta[1] || ci!==32'h0000006f || rd!==0)
                        $fatal(1,"official terminal loop not reached");
                    loops=loops+1;
                end
                // Depois do NBA, confirma o dado realmente armazenado no Register File.
                #1;
                if(finished && dut.core.register_file.regs[4]!==0)
                    $fatal(1,"official x4 not stored");
                if(loops==3) begin
                    if(seen!=={44{1'b1}} || crc_count!=meta[5])
                        $fatal(1,"incomplete official execution coverage=%h crc=%0d",seen,crc_count);
                    $display("PASS official_firmware: x4=00000000, %0d retirements, %0d cycles, CRC=%0d, ISA=44, terminal loop verified",n,cycles,crc_count);
                    $finish;
                end
            end else #1;
        end
        $fatal(1,"official timeout; initial x4=0 is not success");
    end
endmodule
