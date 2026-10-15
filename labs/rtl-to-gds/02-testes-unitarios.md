# 2 — Testes unitários: uma ALU, do vetor ao PASS

[Anterior](01-visao-geral.md) · [Índice](README.md) · [Próxima](03-testes-integracao.md)

## Objetivo e arquivos

Executar a ALU manualmente e reconhecer o mesmo teste automatizado. Abra
[alu.sv](../../rtl/alu.sv), [tb_alu.sv](../../tb/unit/tb_alu.sv) e
[vectors.py](../../scripts/sim/vectors.py).

## Entenda a bancada

A ALU não tem clock: mudar `a_i`, `b_i` ou `op_i` muda a saída combinacional.
`op_i=1` seleciona ADD e `op_i=2` seleciona SUB. O seletor é um controle interno
da ALU, não o opcode completo de uma instrução RISC-V.

A bancada conecta as entradas ao módulo chamado `dut` (dispositivo sob teste):

Nos arquivos comentados, `initial` executa a sequência uma vez; `always` repete
ações, como gerar clock; `task` agrupa passos reutilizáveis, como aplicar um caso.
`$fatal` encerra com erro; `$display` informa PASS e `$finish` encerra normalmente.

```systemverilog
// Saída observada da ALU; expected vem do arquivo de vetores.
alu dut(.a_i(a), .b_i(b), .op_i(op), .result_o(result));
```

Cada linha de `alu.vec` contém quatro campos hexadecimais:

```text
a         b         op  esperado
00000001  00000002  1   00000003
ffffffff  00000001  1   00000000
```

Essas são ilustrações do formato; o segundo caso mostra truncamento em 32 bits.
O testbench usa `$fscanf` para ler os quatro campos, aguarda `#1` (1 ns neste TB)
e faz a comparação. Esse atraso permite estabilizar a simulação; não mede o atraso
físico de uma ALU fabricada.

```systemverilog
// !== trata X/Z como diferenças em vez de deixar o erro passar despercebido.
if (result !== expected)
    $fatal(1, "ALU op=%h a=%h b=%h got=%h expected=%h", op,a,b,result,expected);
```

## Execução manual

Na raiz do projeto, execute em sequência e pare se um comando falhar:

```bash
python3 scripts/sim/vectors.py
head -n 5 build/alu.vec
wc -l build/alu.vec
iverilog -g2012 -Wall -s tb_alu -o build/lab_tb_alu rtl/alu.sv tb/unit/tb_alu.sv
vvp build/lab_tb_alu
```

O gerador cria `build/` e os vetores. `iverilog` compila e elabora o modelo:
`-g2012` seleciona SystemVerilog, `-Wall` habilita avisos, `-s` escolhe o top e
`-o` define o arquivo executado pelo `vvp`. Esse arquivo não é uma netlist física.

O resultado esperado é `PASS alu: 18304 vectors`. São 144 pares de limites e
1.000 pares pseudoaleatórios, multiplicados por 16 seletores. Onze seletores
representam operações válidas; os cinco restantes verificam o retorno padrão zero.

Essa execução manual imprime no terminal. Os logs padronizados serão produzidos
quando você usar o executor:

```bash
make tb TB=tb_alu
cat results/logs/tb_alu.compile.log
cat results/logs/tb_alu.log
```

Compare os comandos: o executor fornece todos os arquivos `rtl/*.sv`, mas mantém
`-s tb_alu` para escolher a bancada. O comportamento verificado é o mesmo.

## Aplique aos demais blocos

Execute um comando por vez. Os arquivos ficam em `tb/unit/` com esses nomes:

```bash
make tb TB=tb_regfile
make tb TB=tb_imm_ext
make tb TB=tb_pc
make tb TB=tb_ir
make tb TB=tb_imem
make tb TB=tb_branch_comp
make tb TB=tb_lsu
make tb TB=tb_dmem
make tb TB=tb_address_decoder
make tb TB=tb_multiplier
make tb TB=tb_decoder
make tb TB=tb_control_unit
make tb TB=tb_crc
```

RF, PC, IR e DMEM também exigem observar bordas de clock e retenção de estado.
Nem todo TB usa arquivos `.vec`: alguns geram estímulos diretamente no SystemVerilog.
Para repetir os 14 testes de uma vez, use `make unit` (ordem alfabética do executor).
`tb_crc` usa o contrato CMOS provisório; seu PASS não confirma o algoritmo oficial
da competição. Os comentários explicam entradas, referência e comparações em cada TB.

## Investigação de falhas

| Mensagem | Primeira investigação |
|---|---|
| `missing vectors` | gerador executado e terminal na raiz? |
| `malformed vector` | linha contém os quatro campos esperados? |
| `got=... expected=...` | qual operação e quais operandos divergiram? |
| diagnóstico de compilação | leia `.compile.log`; a simulação pode nem ter começado |
| `insufficient vectors` | arquivo truncado ou conjunto errado de vetores? |

## Exercício e critério para avançar

Preveja ADD com `a=0x7fffffff`, `b=1`. Resultado: `0x80000000`; a ALU conserva
32 bits, sem criar automaticamente uma exceção de overflow. Avance quando souber
localizar entradas, referência e comparação e tiver o teste da ALU em PASS.
