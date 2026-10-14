`timescale 1ns/1ps
module tb_multiplier;
    // Testa partes baixa/alta do produto e combinações signed/unsigned da Zmmul.
    reg [31:0] a,b,expected;
    reg [3:0] op;
    wire [31:0] result;
    integer fd,status,n;
    multiplier dut(a,b,op,result);
    initial begin
        // Cada vetor contém a, b, operação e resultado inteiro previsto pelo Python.
        fd=$fopen("build/multiplier.vec","r"); n=0;
        if(!fd) $fatal(1,"missing multiplier vectors");
        while(!$feof(fd)) begin
            // Aplica entradas e aguarda #1 antes de comparar a saída combinacional.
            status=$fscanf(fd,"%h %h %h %h\n",a,b,op,expected);
            if(status!=4) $fatal(1,"bad vector");
            #1; if(result!==expected) $fatal(1,"multiply op=%h a=%h b=%h got=%h expected=%h",op,a,b,result,expected);
            n=n+1;
        end
        if(n<10000) $fatal(1,"insufficient vectors");
        // PASS só aparece após todas as comparações; qualquer diferença usa $fatal.
        $display("PASS multiplier: %0d signed/mixed/unsigned high/low vectors",n); $finish;
    end
endmodule
