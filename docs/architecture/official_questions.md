# Definições oficiais necessárias para continuar

Atualização **20/10/2026**: o usuário encaminhou mensagens atribuídas à organização
confirmando CRC-16-CCITT-FALSE nas três instruções e firmware assembly a ser
carregado na IMEM. Veja o [registro e a comparação com o RTL](clarifications_20261020.md).
P01 está parcialmente esclarecida; P02–P04 seguem abertas. O firmware oficial
ainda não foi recebido. O [contrato CRC atual](crc_provisional.md) permanece opt-in
até confirmar a semântica dos operandos, sem ampliar a cobertura oficial.
O retorno será registrado no [formulário de confirmação CRC](crc_official_confirmation.md),
com origem, exemplos e critérios de integração. O programa oficial terá o
[checklist de recebimento](../../firmware/official/receipt.md) preenchido antes da carga.

Referências a páginas físicas de `Champion-chip-guia-fase-2.pdf` (arquivo de 24 páginas).

1. **Xicrc — pp.12,14–15, tabelas 8 e 11.** As codificações de CRCB/CRCH/CRCW estão
   confirmadas. A mensagem de 20/10 identifica CRC-16-CCITT-FALSE e dados de
   8/16/32 bits, sempre com resultado de 16 bits. O nome resolve polinômio,
   reflexão, inicialização da mensagem e XOR final. Falta confirmar papel de
   rs1/rs2, aplicação da semente por instrução/fluxo, ordem dos bytes e
   preenchimento de rd[31:16]. Confrontar pseudocódigo/vetores, incluindo os
   três exemplos registrados, antes de promover o contrato CMOS a oficial.
2. **Sistema/sincronização — p.2.** A tabela exige 3 instruções sem enumerá-las.
   Confirmar nomes, codificações e comportamento esperado, inclusive se há
   parada, trap ou protocolo específico com o firmware/testbench.
3. **Firmware oficial — p.4.** A mensagem de 19/10 prevê publicação após autorização:
   testes assembly de todas as instruções, convertidos em instruções para a IMEM.
   Programas próprios estão autorizados enquanto isso. Faltam o arquivo,
   formato/build, eventual imagem de dados e protocolo de sucesso/falha.
   O demo próprio valida a infraestrutura, mas não fecha esse entregável.
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
as mensagens de 19–20/10 complementam essa situação, sem novo PDF local.

Após resolver as lacunas restantes: fechar CRC isolado → integração e regressão → sistema → 47/47 →
firmware oficial → interface final e entregáveis → OpenLane → GDSII, mantendo
a prioridade e os critérios de conclusão do AGENTS.md.
