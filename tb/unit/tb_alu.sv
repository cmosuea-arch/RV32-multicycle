`timescale 1ns/1ps
module tb_alu;
    reg [31:0] a, b, expected;
    reg [3:0] op;
    wire [31:0] result;
    integer fd, count, status;
    alu dut(.a_i(a), .b_i(b), .op_i(op), .result_o(result));
    initial begin
        fd = $fopen("build/alu.vec", "r");
        if (!fd) $fatal(1, "missing vectors");
        count = 0;
        while (!$feof(fd)) begin
            status = $fscanf(fd, "%h %h %h %h\n", a, b, op, expected);
            if (status != 4) $fatal(1, "malformed vector");
            #1;
            if (result !== expected)
                $fatal(1, "ALU op=%h a=%h b=%h got=%h expected=%h", op,a,b,result,expected);
            count = count + 1;
        end
        if (count < 10000) $fatal(1, "insufficient vectors");
        $display("PASS alu: %0d vectors", count);
        $finish;
    end
endmodule
