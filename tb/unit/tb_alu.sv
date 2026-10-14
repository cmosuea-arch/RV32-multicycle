`timescale 1ns/1ps
module tb_alu;
    // Compara cada operação da ALU com o resultado calculado pelo modelo Python.
    reg [31:0] a, b, expected;
    reg [3:0] op;
    wire [31:0] result;
    integer fd, count, status;
    // DUT: circuito sob teste; a bancada controla as entradas e observa a saída.
    alu dut(.a_i(a), .b_i(b), .op_i(op), .result_o(result));
    initial begin
        // Os vetores Python contêm operandos, seletor e referência independente do RTL.
        fd = $fopen("build/alu.vec", "r");
        if (!fd) $fatal(1, "missing vectors");
        count = 0;
        while (!$feof(fd)) begin
            // Lê quatro campos hexadecimais; status informa quantos foram lidos.
            status = $fscanf(fd, "%h %h %h %h\n", a, b, op, expected);
            if (status != 4) $fatal(1, "malformed vector");
            // Aguarda a propagação simulada; !== também detecta bits X/Z na saída.
            #1;
            if (result !== expected)
                $fatal(1, "ALU op=%h a=%h b=%h got=%h expected=%h", op,a,b,result,expected);
            count = count + 1;
        end
        // Evita declarar sucesso se o arquivo contiver poucos casos por engano.
        if (count < 10000) $fatal(1, "insufficient vectors");
        $display("PASS alu: %0d vectors", count);
        // $display informa o sucesso ao executor; $finish encerra a simulação.
        $finish;
    end
endmodule
