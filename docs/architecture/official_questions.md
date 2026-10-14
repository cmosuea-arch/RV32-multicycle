# Definições oficiais necessárias para continuar

Atualização 2026-10-13: existe um [contrato CRC interno provisório](crc_provisional.md)
autorizado para desenvolvimento. Ele não encerra as perguntas abaixo.

Referências a páginas físicas de `Champion-chip-guia-fase-2.pdf` (arquivo de 24 páginas).

1. **Xicrc — pp.12,14–15, tabelas 8 e 11.** As codificações de CRCB/CRCH/CRCW estão
   confirmadas. Precisamos do polinômio CRC-16, direção/reflexão do processamento,
   ordem dos bytes, papel de rs1/rs2 (dados versus acumulador), seed/xor final e
   preenchimento de rd[31:16]. Um pseudocódigo oficial ou vetores de entrada/saída
   de cada instrução permite implementar e verificar sem escolher uma variante
   de CRC por suposição.
2. **Sistema/sincronização — p.2.** A tabela exige 3 instruções sem enumerá-las.
   Confirmar nomes, codificações e comportamento esperado, inclusive se há
   parada, trap ou protocolo específico com o firmware/testbench.
3. **Firmware oficial — p.4.** Obter arquivos da plataforma, instruções de build,
   imagem de ROM/dados se fornecida e protocolo de sucesso/falha. O demo próprio
   valida a infraestrutura, mas não fecha esse entregável.
4. **Top físico — pp.9–10.** A figura mostra UART/GPIO, enquanto a tabela de
   portas lista apenas clock/reset. Confirmar interface exigida, periféricos,
   mapa de registradores e contratos elétricos/lógicos antes do top de submissão.

Consulta pública feita em 2026-09-11 com termos ChampionCHIP/ChipInventor/Xicrc/
firmware não encontrou complemento oficial. Isso não prova inexistência de
material na plataforma restrita. O Ibex não resolve essas definições da competição.

Após recebê-las: fechar CRC isolado → integração e regressão → sistema → 47/47 →
firmware oficial → interface final e entregáveis → OpenLane → GDSII, mantendo
a prioridade e os critérios de conclusão do AGENTS.md.
