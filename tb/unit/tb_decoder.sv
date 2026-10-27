`timescale 1ns/1ps
module tb_decoder;
    // Compara os sinais de controle com CRC desabilitado e habilitado.
    reg [31:0] instr;
    // programs.py produz instrução + controles: bit 14 é trap_request, bit 0 é illegal.
    reg [14:0] expected;
    wire [3:0] alu_op;
    wire a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal;
    wire crc_op,experimental_crc,trap_request,without_trap;
    wire [13:0] experimental_control;
    integer fd,n,status;
    decoder dut(instr,alu_op,a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal,crc_op,trap_request);
    // Segundo decoder recebe a mesma instrução; suas saídas formam um vetor de controle.
    decoder #(.EXPERIMENTAL_XICRC(0)) without_crc(
        instr,experimental_control[13:10],experimental_control[9],experimental_control[8],
        experimental_control[7],experimental_control[6],experimental_control[5],
        experimental_control[4],experimental_control[3],experimental_control[2],
        experimental_control[1],experimental_control[0],experimental_crc,without_trap);
    initial begin
        // O perfil padrão contém 47 tipos; o segundo mantém 44, removendo apenas CRC.
        fd=$fopen("build/decoder.vec","r"); n=0;
        if(!fd) $fatal(1,"missing decoder vectors");
        while(!$feof(fd)) begin
            status=$fscanf(fd,"%h %h\n",instr,expected);
            if(status!=2) $fatal(1,"bad decoder vector");
            #1;
            // Só as três codificações CRC podem mudar quando o parâmetro é zero.
            if(instr[6:0]==7'h33 && instr[31:25]==7'h40 && instr[14:12]<=2) begin
                if(experimental_control!==14'h0001 || experimental_crc!==0 || crc_op!==1 || without_trap!==0)
                    $fatal(1,"CRC decode failed instr=%h",instr);
            end else if({without_trap,experimental_control}!==expected || experimental_crc!==0 || crc_op!==0)
                $fatal(1,"experimental decode changed non-CRC instr=%h",instr);
            if({trap_request,alu_op,a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal}!==expected)
                $fatal(1,"decode instr=%h got=%h expected=%h",instr,{alu_op,a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal},expected);
            n=n+1;
        end
        // Além da varredura de campos, há duas palavras SYSTEM e 64 vizinhas de um bit.
        if(n!=131138) $fatal(1,"incomplete decode sweep");
        $display("PASS decoder: 131138 words, exact SYSTEM and neighbors, Xicrc enabled and disabled"); $finish;
    end
endmodule
