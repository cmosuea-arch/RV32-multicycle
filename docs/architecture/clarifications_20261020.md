# Esclarecimentos recebidos — 20/10/2026

**Registro histórico.** Em 27/10 o usuário forneceu o repositório do firmware:
[nova análise](crc_official_20261027.md). Ele resolve operandos/bytes de forma
diferente do contrato CMOS abaixo. Esta revisão de 20/10 não é a especificação
final nem um resultado de execução do firmware oficial.

Fonte: mensagens atribuídas à organização e transcritas pelo usuário nesta data.
São um complemento ao Block Guide local, sem constituir nova edição do PDF.
O firmware oficial ainda não foi recebido. Esta revisão não altera RTL,
codificações, habilitação do CRC nem a cobertura registrada de **41/47 (87,23%)**.

## Firmware — mensagem de 19/10/2026

- A publicação está prevista, sujeita à autorização mencionada na mensagem,
  sem data de disponibilização confirmada.
- Será um programa de testes em assembly para exercitar todas as instruções.
- A equipe pode usar programas próprios, por instrução ou integrados, enquanto
  aguarda o oficial. O programa deve virar código de máquina carregado na IMEM.

O fluxo atual já faz essa carga: `build_firmware.py` compila C/startup assembly,
liga com `link.ld`, extrai o binário e gera `build/smoke.hex`; `imem.sv` lê as
palavras com `$readmemh`. O caminho do `simple_system` produz `build/simple.hex`.
Separadamente, `programs.py` monta diretamente palavras de instruções para
`build/isa.hex`, com trace esperado para o TB, sem depender do compilador C.
Esses mecanismos atendem à forma geral de carga descrita, mas o protocolo de
sucesso do teste oficial ainda precisa ser conhecido.

Quando o arquivo chegar: conferir formato e ponto de entrada, bases/capacidades,
eventuais dados iniciais da DMEM, necessidade de conversão e indicação de
sucesso/falha. Não usar a assinatura CMOS como se já fosse o protocolo oficial.

## CRC — mensagem de 20/10/2026

| Instrução | Dados processados | Algoritmo | Resultado útil |
|---|---|---|---|
| CRCB | 8 bits | CRC-16-CCITT-FALSE | 16 bits |
| CRCH | 16 bits | CRC-16-CCITT-FALSE | 16 bits |
| CRCW | 32 bits | CRC-16-CCITT-FALSE | 16 bits |

As referências a CRC8/CRC16/CRC32 nas tabelas 8/11 indicam a quantidade de
dados processados; não são três larguras diferentes de polinômio/resultado.
O Block Guide já está no PDF combinado local, páginas físicas 6–23.

Os parâmetros associados ao nome CCITT-FALSE (também IBM-3740) são:

| Parâmetro | Valor |
|---|---|
| Largura | 16 |
| Polinômio | `0x1021` |
| Inicialização de uma mensagem | `0xFFFF` |
| Reflexão de entrada / saída | `false` / `false` |
| XOR final | `0x0000` |
| Check ASCII `123456789` | `0x29B1` |

Referências técnicas: [catálogo CRC RevEng](https://reveng.sourceforge.io/crc-catalogue/16.htm#crc.cat.crc-16-ibm-3740)
e [Python binascii.crc_hqx](https://docs.python.org/3/library/binascii.html#binascii.crc_hqx),
consultados em 20/10/2026. A biblioteca calcula a atualização com polinômio
`0x1021` a partir do acumulador fornecido; a semente da mensagem é passada pelo software.

## Comparação com a implementação atual

O RTL já implementa atualização de CRC16 com `0x1021`, sem reflexão/XOR final,
seleção de 1/2/4 bytes e resultado de 16 bits estendido com zeros. O firmware
próprio começa em `0xFFFF` e encadeia os resultados. Esses pontos correspondem
à variante informada. No contrato CMOS, `rs1[15:0]` é o acumulador e os bytes
baixos de `rs2` entram primeiro.

A mensagem não especifica qual registrador contém dados/acumulador, se a
inicialização ocorre no software ou em cada instrução, a ordem dos bytes de
CRCH/CRCW e o preenchimento de `rd[31:16]`. A tabela do PDF usa
`CRC8/16/32(rs1, rs2)[15:0]`, sem pseudocódigo que resolva esses pontos.
Reflexão de bits e ordem de bytes de uma palavra são questões distintas.

Exemplos do contrato **atual**, para confrontar com a organização:

| Instrução | rs1 | rs2 | Bytes processados | rd |
|---|---|---|---|---|
| CRCB | `0x0000FFFF` | `0x00000031` | `31` | `0x0000C782` |
| CRCH | `0x0000FFFF` | `0x00003231` | `31 32` | `0x00003DBA` |
| CRCW | `0x0000FFFF` | `0x34333231` | `31 32 33 34` | `0x00005349` |

Pergunta para fechar P01: confirmar esses exemplos e a continuação usando o
resultado como `rs1` da instrução seguinte, ou fornecer pseudocódigo/vetores.
Até isso ser resolvido, o algoritmo está identificado, mas a compatibilidade
completa das instruções permanece pendente e `EXPERIMENTAL_XICRC` continua opt-in.

## Alcance desta revisão

Foi relido o PDF local (SHA-256
`3107f22f7153aca25ea8f472be4dff7474b5c6b9b5b1f0d490da190f5e85ab41`),
especialmente as páginas 2–4, 12 e 14–15. O modelo Python reproduziu os três
exemplos acima e `0x29B1` com a mensagem agrupada em bytes, halfwords e words.
Isso é uma conferência do modelo, sem nova regressão RTL ou execução física.
P01 foi reduzida; P02 (sistema), P03 (arquivo/protocolo do firmware) e P04
(interface final) seguem abertas, conforme [questões oficiais](official_questions.md).
