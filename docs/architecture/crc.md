# Xicrc — contrato implementado e verificado em 27/10/2026

Fonte: [firmware oficial, revisão edc7d599](crc_official_20261027.md).
O contrato histórico CMOS foi substituído. Adequação em `isa-44-v1`;
integração atual em `isa-47-v1`. Evidências:
[47/47 e firmware oficial](../../results/experiments/isa-47-20261027/README.md).

| Instrução | Opcode | Funct7 | Funct3 | Dados de rs1 |
|---|---|---|---|---|
| CRCB | 0x33 | 0x40 | 0 | bits 7:0 |
| CRCH | 0x33 | 0x40 | 1 | bits 15:0 |
| CRCW | 0x33 | 0x40 | 2 | bits 31:0 |

- `rs1` / `a_i`: dados; bits acima do tamanho selecionado são ignorados.
- `rs2[15:0]` / `b_i[15:0]`: CRC anterior; bits altos são ignorados.
- Polinômio 1021, sem reflexão ou XOR final. Processar bytes mais significativos
  primeiro dentro do tamanho selecionado, e MSB primeiro dentro de cada byte.
- `rd = zero_extend_32(crc16)`. Não há estado CRC oculto.
- O software fornece FFFF na primeira operação da mensagem e reutiliza o resultado
  como rs2 da seguinte. Não reinicializar a semente dentro de toda instrução.
- Op 3–15 retorna zero no bloco isolado; funct3 3–7 é ilegal no decoder.
- Sobreposição de rd/rs1/rs2 é permitida; a proteção de x0 permanece no RF.

Exemplo: `CRCW rd, rs1, rs2` com rs1=12345678 e rs2=0000FFFF processa 12 34 56 78.
Ao continuar com rs1=90ABCDEF e rs2=resultado anterior, o resultado é 00001E82.
A memória permanece little-endian: a ordem dos bytes do CRC é definida sobre
o valor carregado no registrador, sem mudar a LSU ou o mapa de memória.

## Implementação e perfil

O bloco é combinacional, com até 32 passos lógicos. O core captura o resultado
em EXECUTE e escreve em WRITEBACK, sem novos estados ou ciclos internos do CRC.
O modelo independente usa `binascii.crc_hqx` sobre bytes em ordem big-endian do
tamanho selecionado, com o acumulador fornecido.

`EXPERIMENTAL_XICRC` mantém o nome histórico por compatibilidade. Seu padrão em
decoder/core/top agora é **1**, com o contrato oficial. Valor 0 desabilita CRC e
mantém os outros 44 tipos, incluindo FENCE/ECALL/EBREAK; a varredura do decoder
testa as duas escolhas. O perfil padrão em `enabled.json` contém **47/47 (100%)**
sob o [EEI CMOS](system.md). O firmware publicado exercita 44 tipos, sem as três
instruções de sistema, que possuem testes próprios. Antes de implementar sistema,
desabilitar CRC deixava 41 instruções; essa contagem é histórica.

## Verificação

- Unidade: 18.304 vetores, seed/dados aleatórios, bits altos, operações inválidas,
  ASCII 123456789 → 29B1 e mensagem oficial → 1E82 em byte/halfword/word.
- Core CRC: 32.930 aposentadorias, 2.146 operações CRC, aliases de registradores,
  x0, seis mensagens/agrupamentos na RAM, load/store e reset.
- ISA integrada: 88.794 aposentadorias comparadas com o modelo arquitetural.
- Firmware oficial: 252 aposentadorias, 1.026 ciclos, 16 CRCs e 44 tipos exercitados;
  escrita final de x4=0 e três aposentadorias do loop final confirmadas.
- Teste negativo na [rodada CRC](../../results/experiments/crc-official-20261027/README.md):
  o mesmo firmware rejeitou o bloco anterior em x4=FFFFFFFF.
- Regressão do marco `isa-47-v1`: 33 TBs e lint dos dois tops PASS.
  Síntese da versão atual não executada.

Os 47 tipos têm evidência funcional no ambiente documentado; isso não é prova
formal ou fechamento físico. A síntese histórica do simple_system é de outra versão;
o CRC e a ROM atuais precisam ser sintetizados novamente pelo usuário.
