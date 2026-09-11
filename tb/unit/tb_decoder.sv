`timescale 1ns/1ps
module tb_decoder;
    reg [31:0] instr;
    reg [13:0] expected;
    wire [3:0] alu_op;
    wire a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal;
    integer fd,n,status;
    decoder dut(instr,alu_op,a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal);
    initial begin
        fd=$fopen("build/decoder.vec","r"); n=0;
        if(!fd) $fatal(1,"missing decoder vectors");
        while(!$feof(fd)) begin
            status=$fscanf(fd,"%h %h\n",instr,expected);
            if(status!=2) $fatal(1,"bad decoder vector");
            #1;
            if({alu_op,a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal}!==expected)
                $fatal(1,"decode instr=%h got=%h expected=%h",instr,{alu_op,a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal},expected);
            n=n+1;
        end
        if(n!=131072) $fatal(1,"incomplete decode sweep");
        $display("PASS decoder: 131072 opcode/funct3/funct7 combinations"); $finish;
    end
endmodule
