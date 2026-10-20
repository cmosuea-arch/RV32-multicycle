# Formulário de confirmação do CRC — aguardando retorno

Use este arquivo para registrar a resposta dos responsáveis. Os campos pendentes
não são escolhas novas de implementação e não devem ser preenchidos por suposição.
Contrato em uso: [crc_provisional.md](crc_provisional.md).
Origem do esclarecimento já recebido: [mensagens de 19–20/10](clarifications_20261020.md).

## Origem da próxima resposta

| Campo | Registro |
|---|---|
| Data da resposta | PENDENTE |
| Responsável/canal ou documento | PENDENTE |
| Versão/página/link, se houver | PENDENTE |
| Texto ou pseudocódigo recebido | PENDENTE |

## Contrato a confrontar

| Item | Informação disponível | Confirmação restante |
|---|---|---|
| Nomes e tamanhos | CRCB: 8 bits; CRCH: 16; CRCW: 32; CRC de 16 bits | Confirmados na mensagem de 20/10 |
| Variante | CRC-16-CCITT-FALSE | Confirmada na mensagem de 20/10 |
| Codificação | opcode 0x33; funct7 0x40; funct3 0/1/2 | Confirmada no Block Guide, tabela 8 |
| rs1 | Implementação usa rs1[15:0] como acumulador | PENDENTE |
| rs2 | Implementação usa os 8/16/32 bits baixos como dados | PENDENTE |
| Inicialização | Software fornece FFFF na primeira operação e depois o resultado anterior | PENDENTE |
| Ordem dos bytes | Implementação começa pelo byte menos significativo de rs2 | PENDENTE |
| rd[31:16] | Implementação escreve zero | PENDENTE |

## Pergunta para encaminhar

> Podemos usar rs1 como acumulador e rs2 como dados, começando em rs1=0xFFFF e
> encadeando os resultados? Em CRCW, rs2=0x34333231 deve processar 31 32 33 34,
> nessa ordem? Os 16 bits superiores de rd devem ser zerados?

Exemplos calculados pela **implementação CMOS atual**, para os responsáveis
confirmarem ou corrigirem; não são vetores oficiais recebidos:

| Instrução | rs1 | rs2 | rd atual | rd informado pelos responsáveis |
|---|---|---|---|---|
| CRCB | 0000FFFF | 00000031 | 0000C782 | PENDENTE |
| CRCH | 0000FFFF | 00003231 | 00003DBA | PENDENTE |
| CRCW | 0000FFFF | 34333231 | 00005349 | PENDENTE |

## Quando a resposta chegar

1. Registrar a origem e o pseudocódigo/vetores; distinguir confirmação de hipótese.
2. Comparar com `rtl/crc.sv`, `scripts/sim/crc_model.py` e este formulário.
3. Se houver divergência, ajustar RTL/modelo, os testes e o firmware próprio
   `firmware/simple/main.c`, preservando os casos anteriores que continuem válidos.
4. Registrar vetores oficiais no teste, incluindo operandos, resultado completo,
   inicialização e encadeamento definidos pela organização.
5. Executar, um comando por vez, os testes abaixo e analisar os logs.
6. Atualizar contrato, evidências, perfil habilitado e cobertura apenas após PASS.
   Mudança do perfil padrão exige também conferir decoder/core/top e geradores.

```bash
# No WSL, na raiz; executar depois de incorporar o contrato confirmado.
make tb TB=tb_crc
make tb TB=tb_decoder
make tb TB=tb_core_crc
make simple-system
make regression
```

Os três primeiros comandos verificam unidade, codificação e integração. O
firmware próprio verifica o uso das três operações; a regressão preserva a
baseline anterior. Um retorno sobre CRC não encerra sozinho as instruções de
sistema, o firmware oficial ou os requisitos físicos da competição.
