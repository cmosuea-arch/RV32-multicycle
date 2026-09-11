`timescale 1ns/1ps
module lsu(
    input logic [31:0] address_i,store_i,mem_i,
    input logic [2:0] funct3_i,
    input logic is_store_i,
    output wire [31:0] load_o,store_o,
    output wire [3:0] bw_o,
    output wire misaligned_o,invalid_o
);
    wire valid=is_store_i ? (funct3_i<=2) :
               (funct3_i==0||funct3_i==1||funct3_i==2||funct3_i==4||funct3_i==5);
    wire [4:0] shift={address_i[1:0],3'b0};
    wire [31:0] shifted=mem_i>>shift;
    wire [31:0] mask=(funct3_i[1:0]==0)?32'h000000ff:
                          (funct3_i[1:0]==1)?32'h0000ffff:32'hffffffff;
    wire [3:0] bytes_mask=(funct3_i[1:0]==0)?4'b0001:
                           (funct3_i[1:0]==1)?4'b0011:4'b1111;
    function automatic [31:0] extend(input [31:0] value,input [2:0] f);
        case(f)
            0: extend={{24{value[7]}},value[7:0]};
            1: extend={{16{value[15]}},value[15:0]};
            2: extend=value;
            4: extend={24'b0,value[7:0]};
            5: extend={16'b0,value[15:0]};
            default: extend=0;
        endcase
    endfunction
    assign invalid_o=!valid;
    assign misaligned_o=valid&&((funct3_i[1:0]==1&&address_i[0])||
                              (funct3_i[1:0]==2&&address_i[1:0]!=0));
    assign load_o=valid&&!misaligned_o&&!is_store_i ? extend(shifted,funct3_i) : 32'b0;
    assign store_o=valid&&!misaligned_o&&is_store_i ? (store_i&mask)<<shift : 32'b0;
    assign bw_o=valid&&!misaligned_o&&is_store_i ? bytes_mask<<address_i[1:0] : 4'b0;
endmodule
