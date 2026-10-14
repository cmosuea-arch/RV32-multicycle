`timescale 1ns/1ps
module tb_imem;
    // Testa a ROM combinacional com oito instruções conhecidas de fetch.hex.
    reg [31:0] address=0;
    reg oe=0;
    wire [31:0] data;
    integer i;
    imem #(.WORDS(8),.INIT_FILE("tb/data/fetch.hex")) dut(address,oe,data);
    initial begin
        oe=1;
        for(i=0;i<8;i=i+1) begin
            // Cada palavra é ADDI x1,x0,i+1; endereços avançam de quatro em quatro bytes.
            address=32'h00400000+4*i; #1;
            if(data!==(32'h00100093+(i<<20))) $fatal(1,"ROM index=%0d",i);
        end
        oe=0; #1; if(data!==0) $fatal(1,"oe"); oe=1;
        // Endereços fora da ROM e endereços desalinhados devem devolver zero.
        address=32'h00400020; #1; if(data!==0) $fatal(1,"upper bound");
        address=32'h003ffffc; #1; if(data!==0) $fatal(1,"lower bound");
        address=32'h00400001; #1; if(data!==0) $fatal(1,"alignment");
        $display("PASS imem: initialized contents, sequential read, bounds and oe"); $finish;
    end
endmodule
