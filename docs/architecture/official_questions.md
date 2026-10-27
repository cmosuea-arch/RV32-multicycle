# Definições oficiais necessárias para continuar

Atualização **27/10/2026**: o usuário forneceu o repositório do firmware oficial.
O uso das instruções resolve a principal lacuna de P01, e o README fornece o
formato IMEM/protocolo de P03. A [análise da revisão consultada](crc_official_20261027.md)
identifica duas divergências do RTL: operandos invertidos e ordem dos bytes.
O [registro do contrato](crc_official_confirmation.md) e o
[recebimento do firmware](../../firmware/official/receipt.md) foram preenchidos.
Adequação, integração e execução foram concluídas em seguida:
[44/47, 32 TBs/lint e firmware oficial PASS](../../results/experiments/crc-official-20261027/README.md).
P01/P03 estão resolvidas para a revisão publicada. A revisão normativa abaixo
identifica os nomes/códigos de P02. O [EEI CMOS](system.md) foi implementado e
validado em seguida: [47/47 e 33 TBs/lint PASS](../../results/experiments/isa-47-20261027/README.md).
P02 passa funcionalmente nesse ambiente; P04 segue aberta.

Referências a páginas físicas de `Champion-chip-guia-fase-2.pdf` (arquivo de 24 páginas).

1. **Xicrc — pp.12,14–15, tabelas 8 e 11.** As codificações de CRCB/CRCH/CRCW estão
   confirmadas. O firmware.s recebido em 27/10 usa rs1=dados, rs2=CRC anterior,
   seed FFFF por software e bytes mais significativos primeiro, exigindo 1E82
   para a mesma mensagem nos três tamanhos. A falta de exemplos está resolvida;
   RTL/modelo/vetores/firmware próprio foram corrigidos e a regressão passou.
2. **Sistema/sincronização — p.2.** A tabela exige 3 instruções sem enumerá-las.
   O Block Guide exige RV32I e referencia o manual oficial (§1.2, p.7;
   §§2.1/2.4, pp.9/11). Essa referência identifica **FENCE, ECALL e EBREAK**,
   com codificações e semântica padronizadas. A
   [revisão normativa](system_audit_20261027.md) corrige a pendência anterior.
   O [EEI CMOS](system.md) define traps terminais separados de FAULT, com PC e
   motivo expostos; FENCE e os dois traps passam em testes próprios. Confirmar
   apenas eventual protocolo adicional exigido pela competição.
3. **Firmware oficial — p.4.** Repositório consultado em 27/10: fonte assembly e
   imagem de 259 palavras para IMEM, início em 00400000; término em x4=0 ou
   FFFFFFFF. A imagem foi convertida/carregada e o TB verifica a escrita final
   mais três commits do loop, sem aceitar o zero do reset. Execução completa PASS.
4. **Top físico — pp.9–10.** A figura mostra UART/GPIO, enquanto a tabela de
   portas lista apenas clock/reset. Confirmar interface exigida, periféricos,
   mapa de registradores e contratos elétricos/lógicos antes do top de submissão.

Consulta pública feita em 2026-09-11 com termos ChampionCHIP/ChipInventor/Xicrc/
firmware não encontrou complemento oficial. Isso não prova inexistência de
material na plataforma restrita. O Ibex não resolve essas definições da competição.

Nova consulta em 2026-10-17 ao [site oficial](https://championchipexperience.org/)
e buscas por Xicrc/firmware/guia não localizaram complemento oficial público
que resolvesse P01–P04. A wiki pública ChipInventor não pôde ser aberta pela
ferramenta de consulta usada. Esses limites não comprovam ausência de material
na plataforma. Implementações de outras equipes não substituem esclarecimento
da organização nem foram usadas para escolher semântica de sistema.

As consultas e a ausência de esclarecimentos em 17/10 são registros históricos;
as mensagens de 19–20/10 e o firmware recebido em 27/10 complementam essa situação,
sem novo PDF local. O firmware consultado contém 44 instruções distintas e não
exercita as três de sistema. Seus nomes/códigos, porém, estão disponíveis no
manual RV32I referenciado pelo Block Guide, conforme a revisão acima.

CRC, sistema/sincronização e firmware oficial passam no ambiente documentado.
Próximas etapas: interface final e diagramas → congelamento da entrega → síntese
e fluxo físico pelo usuário → GDSII e pacote, mantendo os critérios do AGENTS.md.
