# CRC no firmware oficial — revisão de 27/10/2026

**Atualização após a análise:** as diferenças abaixo foram corrigidas. O
[contrato implementado](crc.md) e a
[rodada de validação](../../results/experiments/crc-official-20261027/README.md)
registram 44/47, 32 TBs/lint e firmware oficial PASS. As seções seguintes
preservam a análise anterior às alterações.

Fonte fornecida pelo usuário: repositório
[CCX_Brasil_Edition_Firmware_Stage_2](https://github.com/championchip-experience-community/CCX_Brasil_Edition_Firmware_Stage_2).
Revisão lida: `edc7d5990d2185942081ee8a6899aa603cc91569`.
URLs e SHA-256 dos três arquivos estão em
[firmware/official/source.json](../../firmware/official/source.json).

Esta revisão extrai o contrato e compara o modelo atual. Não altera RTL, modelo,
firmware próprio, parâmetros ou cobertura; não executa síntese nem o firmware
oficial no processador. Os arquivos upstream foram lidos em cópia temporária,
sem transcrever o programa completo para este repositório.

## Contrato demonstrado pelos testes oficiais

O trecho [firmware.s, linhas 279–340](https://github.com/championchip-experience-community/CCX_Brasil_Edition_Firmware_Stage_2/blob/edc7d5990d2185942081ee8a6899aa603cc91569/firmware.s#L279-L340)
testa uma mesma mensagem com as três instruções, reutilizando o resultado como
acumulador. A semente FFFF é colocada em um registrador pelo software.

| Item | Contrato extraído |
|---|---|
| rs1 | Dados: os 8/16/32 bits selecionados pela instrução |
| rs2 | CRC anterior; inicialmente FFFF |
| rd | Resultado CRC16, usado como rs2 na operação seguinte |
| CRCB | Um byte por instrução |
| CRCH | Dois bytes, começando pelo mais significativo da meia palavra |
| CRCW | Quatro bytes, começando pelo mais significativo da palavra |
| Mensagem de referência | 12 34 56 78 90 AB CD EF |
| Resultado final comparado | 00001E82, para os três agrupamentos e o teste com loads |

A conclusão sobre a ordem dos bytes decorre da equivalência exigida: a sequência
de CRCB recebe 12, 34, 56, 78, 90, AB, CD, EF; a de CRCH recebe 1234, 5678,
90AB, CDEF; a de CRCW recebe 12345678 e 90ABCDEF. Todos devem terminar em 1E82.
São bytes mais significativos primeiro dentro de cada valor, mesmo com a
memória do processador organizada em little-endian. O load monta o valor do
registrador; a instrução CRC define a ordem em que seus bits são processados.

O nome CCITT-FALSE, confirmado pela mensagem de 20/10, fornece polinômio 1021,
ausência de reflexão e XOR final zero. O firmware confirma o uso de seed FFFF
por software e o encadeamento. O teste exige igualdade do resultado final de
32 bits com 00001E82; ele não é uma prova exaustiva dos bits altos em todos os
resultados intermediários. Estender o CRC16 com zeros continua sendo a regra
de implementação adequada ao resultado [15:0] do Block Guide.

## Diferenças concretas no projeto atual

| Ponto | RTL/modelo CMOS atual | Uso no firmware oficial |
|---|---|---|
| Acumulador | rs1 / a_i | rs2 / b_i |
| Dados | rs2 / b_i | rs1 / a_i |
| Bytes em CRCH/CRCW | Menos significativo primeiro | Mais significativo selecionado primeiro |

Uma comparação independente com `binascii.crc_hqx` fornece:

| Agrupamento da mensagem oficial | Modelo atual chamado como no firmware | Só operandos corrigidos, ainda com bytes baixos primeiro | Referência compatível com o firmware |
|---|---|---|---|
| 8 CRCB | 1CFF | 1E82 | 1E82 |
| 4 CRCH | 7F5E | 3B43 | 1E82 |
| 2 CRCW | 9395 | CB31 | 1E82 |

Esses números são resultados do **modelo Python**, não de uma execução do core.
Demonstram por que trocar apenas os nomes dos sinais ou apenas os operandos
não resolve CRCH/CRCW. As evidências antigas continuam válidas para o contrato
CMOS histórico e não comprovam conformidade com esse firmware.

## Adequação a realizar, um bloco por vez

1. Atualizar o contrato de `crc.sv`: a_i recebe dados, b_i recebe acumulador;
   processar bits 7→0, 15→0 ou 31→0 conforme op, sem alterar opcode/funct3/funct7.
2. Atualizar o modelo independente e os vetores de unidade, incluindo os três
   agrupamentos oficiais, acumuladores não fixos, bits altos e operações inválidas.
3. Adaptar `crc_vectors.py`, o modelo arquitetural em `programs.py` e o firmware
   próprio de `simple_system`, hoje escritos para operandos e bytes inversos.
4. Executar unidade, decoder, integração CRC, sistema próprio e regressão. Só
   então revisar o perfil padrão, a matriz, os diagramas e o status de M7.
5. Converter `firmware.txt` para uma imagem IMEM preservando endereços e constantes;
   integrar TB com o protocolo oficial de término e executar o programa completo.

O [registro do contrato](crc_official_confirmation.md) agora contém a fonte que
faltava. A pendência deixou de ser obter exemplos: é adequar e verificar a
implementação. A contagem publicada permanece 41/47 enquanto isso.

## Outras informações úteis do repositório

- O [README oficial](https://github.com/championchip-experience-community/CCX_Brasil_Edition_Firmware_Stage_2/blob/edc7d5990d2185942081ee8a6899aa603cc91569/README.md)
  separa o firmware completo de validação do mock pequeno recomendado para um
  teste físico rápido. Não exige embutir o programa completo na síntese.
- `firmware.txt` possui 259 palavras consecutivas, de 00400000 até 00400408:
  254 palavras de código e cinco constantes. As constantes devem continuar
  acessíveis por loads na IMEM.
- O protocolo final é x4=0 para sucesso, x4=FFFFFFFF para falha. Como nosso reset
  já zera x4, o TB deve observar a escrita de término/loop final, sem aceitar
  o zero inicial como PASS. Na imagem publicada, as escritas de sucesso/falha
  estão em 004003E8 e 004003F0, respectivamente.
- A análise estática identifica as 41 instruções baseline e as três CRCs, com
  16 instruções CRC no código. Nenhuma das três instruções de sistema pendentes
  é enumerada ou exercitada. Isso não autoriza trocar a meta 47 do guia por 44.
