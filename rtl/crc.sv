`timescale 1ns/1ps
// Contrato CMOS provisório: CRC-16/0x1021, bytes baixos primeiro, MSB de cada byte primeiro.
module crc(
    input logic [31:0] a_i,b_i,
    input logic [3:0] op_i,
    output reg [31:0] result_o
);
    reg [15:0] remainder;
    integer byte_index,bit_index,byte_count;
    // Circuito combinacional: a traz o acumulador; b traz até quatro bytes novos.
    always @* begin
        remainder=a_i[15:0];
        // O funct3 das instruções provisórias seleciona byte, halfword ou word.
        case(op_i)
            0: byte_count=1;
            1: byte_count=2;
            2: byte_count=4;
            default: byte_count=0;
        endcase
        // Limites constantes permitem síntese; o resultado é capturado em EXECUTE.
        for(byte_index=0;byte_index<4;byte_index=byte_index+1)
            if(byte_index<byte_count) begin
                // Injeta o byte e executa oito passos do polinômio, sem clock interno.
                remainder=remainder ^ {b_i[byte_index*8+:8],8'b0};
                for(bit_index=0;bit_index<8;bit_index=bit_index+1)
                    remainder=remainder[15] ? (remainder<<1)^16'h1021 : remainder<<1;
            end
        // Resultado de 16 bits estendido com zeros; não aplica XOR final.
        result_o=(byte_count==0)?32'b0:{16'b0,remainder};
    end
endmodule
