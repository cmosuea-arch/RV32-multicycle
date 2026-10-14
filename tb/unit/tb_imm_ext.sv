`timescale 1ns/1ps
module tb_imm_ext;
    // Confere reconstrução dos imediatos I/S/B/U/J e extensão de sinal.
    reg [31:0] instr,expected;
    wire [31:0] imm;
    integer fd,n,status;
    imm_ext dut(instr,imm);
    initial begin
        // Cada linha contém instrução codificada e imediato esperado pelo Python.
        fd=$fopen("build/imm.vec","r"); n=0;
        if(!fd) $fatal(1,"missing vectors");
        while(!$feof(fd)) begin
            // $fscanf preenche entradas/referência; #1 permite estabilizar a saída.
            status=$fscanf(fd,"%h %h\n",instr,expected);
            if(status!=2) $fatal(1,"bad vector");
            #1; if(imm !== expected) $fatal(1,"immediate instr=%h got=%h expected=%h",instr,imm,expected);
            n=n+1;
        end
        if(n<5000) $fatal(1,"insufficient vectors");
        // Loads/JALR compartilham formato I; AUIPC compartilha formato U com LUI.
        instr=32'hfff00003; #1; if(imm!==32'hffffffff) $fatal(1,"load immediate");
        instr=32'hfff00067; #1; if(imm!==32'hffffffff) $fatal(1,"jalr immediate");
        instr=32'h80000017; #1; if(imm!==32'h80000000) $fatal(1,"auipc immediate");
        $display("PASS imm_ext: %0d I/S/B/U/J vectors plus opcode aliases",n); $finish;
    end
endmodule
