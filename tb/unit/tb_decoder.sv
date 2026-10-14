`timescale 1ns/1ps
module tb_decoder;
    reg [31:0] instr;
    reg [13:0] expected;
    wire [3:0] alu_op;
    wire a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal;
    wire crc_op,experimental_crc;
    wire [13:0] experimental_control;
    integer fd,n,status;
    decoder dut(instr,alu_op,a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal,crc_op);
    decoder #(.EXPERIMENTAL_XICRC(1)) experimental(
        instr,experimental_control[13:10],experimental_control[9],experimental_control[8],
        experimental_control[7],experimental_control[6],experimental_control[5],
        experimental_control[4],experimental_control[3],experimental_control[2],
        experimental_control[1],experimental_control[0],experimental_crc);
    initial begin
        fd=$fopen("build/decoder.vec","r"); n=0;
        if(!fd) $fatal(1,"missing decoder vectors");
        while(!$feof(fd)) begin
            status=$fscanf(fd,"%h %h\n",instr,expected);
            if(status!=2) $fatal(1,"bad decoder vector");
            #1;
            if(crc_op!==0) $fatal(1,"CRC enabled in baseline");
            if(instr[6:0]==7'h33 && instr[31:25]==7'h40 && instr[14:12]<=2) begin
                if(experimental_control!==14'h0080 || experimental_crc!==1)
                    $fatal(1,"CRC decode failed instr=%h",instr);
            end else if(experimental_control!==expected || experimental_crc!==0)
                $fatal(1,"experimental decode changed non-CRC instr=%h",instr);
            if({alu_op,a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal}!==expected)
                $fatal(1,"decode instr=%h got=%h expected=%h",instr,{alu_op,a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal},expected);
            n=n+1;
        end
        if(n!=131072) $fatal(1,"incomplete decode sweep");
        $display("PASS decoder: 131072 combinations in baseline and experimental CRC profiles"); $finish;
    end
endmodule
