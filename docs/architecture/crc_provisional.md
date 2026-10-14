# CRC CMOS provisório — 2026-10-13

Decisão autorizada pelo usuário para avançar sem o algoritmo oficial. É uma
especificação interna explícita, substituível quando a ChampionCHIP esclarecer
Xicrc. Não representa confirmação de compatibilidade com o firmware oficial.

## Contrato

Mantemos nomes/codificações já registrados do guia, pp.12,14–15, tabelas 8 e 11:

| Instrução | Opcode | Funct7 | Funct3 | Dados processados |
|---|---|---|---|---|
| CRCB | 0x33 | 0x40 | 0 | rs2[7:0] |
| CRCH | 0x33 | 0x40 | 1 | rs2[15:0] |
| CRCW | 0x33 | 0x40 | 2 | rs2[31:0] |

- `rs1[15:0]`: acumulador CRC anterior; bits altos ignorados.
- Polinômio: `x^16 + x^12 + x^5 + 1` (`0x1021`).
- Bytes do menos significativo ao mais significativo; dentro de cada byte,
  bit mais significativo primeiro. Sem reflexão e sem XOR final.
- `rd = zero_extend_32(crc16)`. Os bits altos de rs2 fora do tamanho escolhido
  não participam. Sobreposição de rd/rs1/rs2 é permitida; x0 continua zero.
- Não existe estado CRC oculto nem seed implícita: software fornece rs1.
- Para reproduzir CRC-16/IBM-3740 de um fluxo, iniciar acumulador com `0xffff`.
  A sequência ASCII `123456789` produz `0x29b1`; com seed zero, `0x31c3`.
- Funct3 3–7 com esse funct7 continua ilegal. No bloco isolado, op inválido
  retorna zero; o decoder impede sua aposentadoria como instrução CRC.

Exemplo: `rs2=0x34333231` em CRCW processa `31 32 33 34` (ASCII `1234`).
Isso permite agrupar dados little-endian sem trocar a ordem dos bytes.

## Escolha de implementação

CRC-16/0x1021 possui referência independente na biblioteca padrão de Python,
facilitando testes reproduzíveis sem dependência pip. A arquitetura multiciclo
não escolhe o polinômio. Não afirmamos que este seja o algoritmo oficial ou
o de menor área/atraso.

Nesta primeira versão o bloco é combinacional, com até 32 passos lógicos de
atualização. O core captura o resultado em EXECUTE e escreve em WRITEBACK,
sem novos estados/handshake. Não há 32 ciclos de clock: os laços descrevem lógica.
Uma implementação iterativa só será justificada por resultados de síntese/timing.

## Seleção e rastreabilidade

`EXPERIMENTAL_XICRC=1` em decoder/core/top habilita a extensão. O padrão é zero:
a configuração de referência preserva 41/47 e rejeita essas instruções.
Os testes da extensão são executados na regressão geral, mas seus vetores,
programas, contagens e evidências ficam identificados como provisórios.
`docs/isa/enabled.json` não é ampliado por esse experimento.

Há 41 instruções da baseline e 3 adicionais testadas sob este contrato interno
(44 operações no perfil experimental). A cobertura de conformidade registrada
permanece **41/47 (87,23%)**, até resolver a semântica oficial.

## Referências

- [Python binascii.crc_hqx](https://docs.python.org/3/library/binascii.html#binascii.crc_hqx):
  implementação independente usada no modelo de teste.
- [Catálogo CRC RevEng — IBM-3740](https://reveng.sourceforge.io/crc-catalogue/16.htm#crc.cat.crc-16-ibm-3740):
  parâmetros e check conhecido, consultado em 2026-10-13.
- [Pendências oficiais](official_questions.md): P01 continua aberta.
