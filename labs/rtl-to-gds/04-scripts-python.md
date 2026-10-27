# 4 — Python: referências, entradas e coordenação

[Anterior](03-testes-integracao.md) · [Índice](README.md) · [Próxima](05-makefile.md)

## Objetivo e arquivos

Seguir os arquivos produzidos e consumidos por cada script. Nenhum destes scripts
vira circuito; eles executam no computador de desenvolvimento.

| Script | Entrada principal | Saída ou efeito |
|---|---|---|
| [vectors.py](../../scripts/sim/vectors.py) | limites, seed e modelos inteiros | `alu.vec`, `imm.vec`, `branch.vec`, `lsu.vec`, `multiplier.vec` |
| [isa.py](../../scripts/sim/isa.py) | nome da instrução e operandos | campos e palavra binária; biblioteca importada |
| [programs.py](../../scripts/sim/programs.py) | `enabled.json`, modelos e seed | `isa.hex`, `isa.trace`, `isa_counts.json`, `isa_memory.vec`, `decoder.vec` |
| [build_firmware.py](../../scripts/sim/build_firmware.py) | C, startup e linker script | ELF, binário, ROM hex e disassembly |
| [crc_model.py](../../scripts/sim/crc_model.py) | acumulador, dados e tamanho | referência CRC usando binascii, sem copiar o RTL |
| [crc_vectors.py](../../scripts/sim/crc_vectors.py) | contrato Xicrc oficial e acumulador | `crc.vec`, ROM/trace/contagens CRC separados da baseline |
| [build_simple.py](../../scripts/sim/build_simple.py) | firmware/simple | `simple.elf`, `simple.hex`, mapa e disassembly |
| [run.py](../../scripts/regression/run.py) | modo solicitado e arquivos do projeto | chamadas às ferramentas, logs e manifesto |
| [coverage.py](../../scripts/regression/coverage.py) | instruções habilitadas e contagens | CSV e Markdown; chama o gerador Excel |
| [coverage_xlsx.py](../../scripts/regression/coverage_xlsx.py) | CSV | planilha formatada `.xlsx` |
| [synth/simple.py](../../scripts/synth/simple.py) | RTL e `simple.hex` | netlist Yosys, teste com Icarus/vvp e resumo de síntese |

Os arquivos intermediários da tabela ficam em `build/`; logs e disassembly ficam
em `results/logs/`; a cobertura publicada fica em `docs/isa/`.

## Referência numérica da ALU

Abra `alu_model()` em `vectors.py`. Python usa inteiros sem a largura fixa do
registrador, por isso o resultado recebe `& MASK`, com `MASK=0xffffffff`.
`signed()` interpreta um padrão de bits como complemento de dois. A seed `0xC005`
permite reproduzir os pares pseudoaleatórios; `EDGES` cobre limites explicitamente.

Confira duas previsões sem executar RTL:

```bash
PYTHONPATH=scripts/sim python3 -c 'from vectors import alu_model; print(hex(alu_model(0xffffffff, 1, 1))); print(hex(alu_model(0x80000000, 1, 8)))'
```

Resultado: `0x0` para ADD e `0xc0000000` para shift aritmético à direita.
Isso verifica sua leitura do modelo. A comprovação do circuito exige a comparação
no testbench, como na aula 2.

## Codificação e execução são etapas distintas

`isa.fields()` encontra opcode/funct3/funct7; `isa.encode()` monta a palavra de
instrução. O modelo que executa instruções está em `Program.evaluate()`, em
`programs.py`: ele segue o PC, atualiza registradores/memória e registra o trace.

```bash
PYTHONPATH=scripts/sim python3 -c 'from isa import encode; word=encode("ADD", rd=3, rs1=1, rs2=2); print(f"{word:08x}")'
```

Esse exemplo codifica ADD x3,x1,x2 e resulta em `002081b3`. A palavra identifica
registradores e operação; os valores armazenados em x1/x2 só serão usados na execução.

Gere o programa integrado e inspecione suas duas representações:

```bash
python3 scripts/sim/programs.py
head -n 3 build/isa.hex
head -n 3 build/isa.trace
head -n 10 build/isa_counts.json
```

O `.hex` contém instruções em posições de ROM. O `.trace` contém a sequência de
aposentadorias esperadas, incluindo saltos e repetições. `isa_counts.json` é gerado
pelo modelo; só vira evidência de execução RTL depois que `tb_isa` compara o trace
com o processador. Os modelos Python também podem ter erros; vetores conhecidos,
revisão da especificação e o caminho de compilação por GCC ajudam a conferir isso.

## Firmware compilado

```bash
python3 scripts/sim/build_firmware.py
head -n 20 results/logs/smoke.disasm
cat results/logs/firmware_build.log
```

O script chama GCC com `-march=rv32i_zmmul -mabi=ilp32`, apesar do nome da ferramenta
começar com `riscv64`. O linker script posiciona código e dados; o startup configura
a execução. `objcopy` gera bytes, convertidos em palavras little-endian para
`build/smoke.hex` (4.096 palavras, 16 KiB). Esse comando **compila** o firmware.
`make run` (equivalente a `make tb TB=tb_firmware`) o compila e **executa no RTL**.

Para o sistema experimental, `make simple-firmware` gera `build/simple.hex` com
512 palavras (2 KiB), e `make simple-system` também executa esse programa no RTL.
Os linker scripts e endereços de assinatura dos dois programas são distintos.

## Referência CRC e coordenação da síntese

```bash
PYTHONPATH=scripts/sim python3 -c 'from crc_model import check_reference, crc_model; check_reference(); print(hex(crc_model(0xffff, 0x34333231, 2)))'
```

`check_reference()` confere os valores conhecidos de `123456789` com duas seeds.
`crc_model()` processa os bytes de `1234` e devolve `0x5349`. O gerador usa essa
referência para alimentar `tb_crc` e o programa de `tb_core_crc`, sem alterar
`enabled.json` nem a cobertura de conformidade.

`scripts/synth/simple.py` coordena outras ferramentas: Yosys gera o circuito,
Python verifica sua estrutura e Icarus/vvp executam o teste da netlist. O Python
continua sendo o coordenador; o circuito vem do RTL. A execução guiada está na
[aula 7](07-sintese.md).

## Leia o coordenador run.py

Siga estas regiões no arquivo:

1. `run()`: usa `subprocess.run` para chamar uma ferramenta, guardar stdout/stderr
   e reprovar código de saída não zero ou timeout de 120 s por processo.
2. `argparse`: lê modo e nome da bancada; os modos principais são exclusivos.
3. Preparação: cria pastas e executa os geradores necessários. Atualmente a seleção
   individual também gera programas, mesmo para um teste que não os consome.
4. Descoberta: encontra `tb_*.sv`, ordena e filtra por suíte/nome.
5. Laço dos TBs: compila com `iverilog`, executa com `vvp`, exige a marca `PASS`.
6. Fechamento: opcionalmente roda lint; em execução completa publica cobertura e
   manifesto com hashes.

O lint elabora `riscv_top` e `simple_system` separadamente. A síntese genérica
tem outro script e outro resumo: `simple_synth.json`, sem substituir `regression.json`.

```bash
python3 scripts/regression/run.py --test tb_alu
cat results/logs/tb_alu.compile.log
cat results/logs/tb_alu.log
```

Resultado esperado: somente a bancada selecionada em PASS. Um `PASS` impresso pelo
gerador significa que os dados foram gerados; a aprovação do RTL vem dos TBs.

## Exercício e critério para avançar

Localize onde `--wave` acrescenta `+WAVE` ao `vvp` e onde o testbench lê esse argumento.
Resposta: laço de simulação em `run.py` e `$test$plusargs("WAVE")` em `tb_firmware`.
Avance quando conseguir explicar o produtor e o consumidor de `alu.vec`, `isa.trace`
e `smoke.hex` sem confundir geração de referência com simulação.
