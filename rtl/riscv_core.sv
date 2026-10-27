`timescale 1ns/1ps
// Datapath multiciclo sem memórias internas: usa um barramento para fetch e dados.
// Os sinais commit permitem ao TB comparar cada instrução concluída com o modelo.
module riscv_core #(
    parameter bit EXPERIMENTAL_XICRC=1
)(
    input logic clk_i,rst_i,
    input logic [31:0] data_i,
    input logic bus_fault_i,
    output wire [31:0] address_o,data_o,
    output wire oe_o,we_o,
    output wire [3:0] bw_o,
    output wire fault_o,commit_valid_o,
    output wire [31:0] commit_pc_o,commit_instr_o,commit_data_o,
    output wire [4:0] commit_rd_o
);
    localparam [2:0] FETCH=0,EXECUTE=2,WRITEBACK=3,MEMORY=4,FAULT=5;
    wire [2:0] state;
    wire [31:0] current_pc,plus4,instruction,immediate,a,b,alu_result;
    // Registradores entre EXECUTE e WRITEBACK: guardam resultado/endereço e próximo PC.
    reg [31:0] result_q,next_pc_q;
    wire branch_taken;
    // JALR limpa o bit zero; branches só redirecionam quando o comparador aprova.
    wire [31:0] redirect_target=jalr?{alu_result[31:1],1'b0}:alu_result;
    wire redirect=(branch&&branch_taken)||jal||jalr;
    wire [3:0] alu_op;
    wire a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal;
    wire [31:0] load_data,store_data;
    wire [31:0] product;
    wire crc_op;
    wire [31:0] crc_result;
    wire [3:0] store_bw;
    wire misaligned,lsu_invalid;
    // Load usa a leitura da DMEM; as demais escritas usam o resultado já registrado.
    wire [31:0] writeback_data=load?load_data:result_q;
    wire retire=(state==WRITEBACK)&&!rst_i;
    // Falhas são avaliadas no estado em que o endereço correspondente está válido.
    wire local_fault=((state==FETCH)&&(bus_fault_i || current_pc[1:0]!=0)) ||
                     ((state==EXECUTE)&&redirect&&redirect_target[1:0]!=0) ||
                     ((state==MEMORY)&&(bus_fault_i||misaligned||lsu_invalid));
    // A FSM define quando agir; o decoder define qual operação a instrução pede.
    control_unit control(clk_i,rst_i,illegal,load,store_op,local_fault,state);
    decoder #(.EXPERIMENTAL_XICRC(EXPERIMENTAL_XICRC)) decode(
        instruction,alu_op,a_pc,b_imm,reg_we,branch,jal,jalr,load,store_op,mul,illegal,crc_op);
    // PC e RF mudam em WRITEBACK; IR captura em FETCH e retém a instrução depois.
    pc program_counter(clk_i,rst_i,retire,next_pc_q,current_pc,plus4);
    ir instruction_register(clk_i,rst_i,state==FETCH&&!local_fault&&!rst_i,data_i,instruction);
    imm_ext immediate_ext(instruction,immediate);
    regfile register_file(clk_i,rst_i,retire&&reg_we,instruction[19:15],instruction[24:20],instruction[11:7],writeback_data,a,b);
    // Muxes escolhem PC ou rs1 para A, imediato ou rs2 para B da ALU.
    alu arithmetic(a_pc?current_pc:a,b_imm?immediate:b,alu_op,alu_result);
    branch_comp branch_compare(a,b,instruction[14:12],branch_taken);
    lsu load_store(result_q,b,data_i,instruction[14:12],store_op,load_data,store_data,store_bw,misaligned,lsu_invalid);
    multiplier multiply(a,b,{1'b0,instruction[14:12]},product);
    // Nome de parâmetro preservado por compatibilidade; 0 seleciona o subconjunto sem CRC.
    generate if(EXPERIMENTAL_XICRC) begin : gen_crc
        crc checksum(a,b,{1'b0,instruction[14:12]},crc_result);
    end else begin : gen_no_crc
        assign crc_result=32'b0;
    end endgenerate
    // Captura em EXECUTE evita depender de resultados combinacionais nos ciclos seguintes.
    // Jumps guardam PC+4 para rd, embora a ALU tenha calculado o endereço do salto.
    always @(posedge clk_i) begin
        if(rst_i) begin result_q<=0; next_pc_q<=0; end
        else if(state==EXECUTE) begin
            result_q<=(jal||jalr)?plus4:crc_op?crc_result:mul?product:alu_result;
            next_pc_q<=redirect?redirect_target:plus4;
        end
    end
    // Barramento compartilhado: PC no fetch; endereço efetivo registrado no acesso a dados.
    assign address_o=(state==MEMORY||(state==WRITEBACK&&(load||store_op)))?result_q:current_pc;
    assign data_o=store_data;
    // Load mantém a leitura até WRITEBACK; store escreve apenas na borda de MEMORY.
    assign oe_o=!rst_i&&((state==FETCH)||((state==MEMORY||state==WRITEBACK)&&load&&!misaligned&&!lsu_invalid));
    assign we_o=!rst_i&&state==MEMORY&&store_op&&!misaligned&&!lsu_invalid;
    assign bw_o=we_o?store_bw:4'b0;
    assign fault_o=state==FAULT;
    // Dados de commit só descrevem uma conclusão quando commit_valid_o está em 1.
    assign commit_valid_o=retire;
    assign commit_pc_o=current_pc;
    assign commit_instr_o=instruction;
    assign commit_rd_o=reg_we?instruction[11:7]:5'b0;
    assign commit_data_o=(commit_rd_o==0)?32'b0:writeback_data;
endmodule
