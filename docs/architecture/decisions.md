# Decisões arquiteturais

Data: 2026-09-11. Baseline inicial: `baseline-v1`.

1. Clock de subida, reset síncrono ativo alto. Guia nomeia clk_i/rst_i mas não
   define polaridade/tipo. Reset limpa RF, IR e registradores internos e reinicia
   PC em IMEM_BASE. DMEM não é apagada. Reset suprime escrita de memória.
2. PC retido durante a instrução; atualização somente em WRITEBACK. A frase do
   guia sobre incremento a cada clock não pode ser literal numa FSM multiciclo.
3. IMEM combinacional, DMEM síncrona conforme §4.3. Um estado MEMORY acomoda a
   latência; não há pipeline, stalls externos, CSRs, debug ou arquitetura Ibex.
4. Acessos desalinhados, endereços não mapeados, escrita na ROM e instruções não
   suportadas produzem FAULT persistente sem writeback/escrita. É diagnóstico
   interno CMOS, NÃO implementação de traps privilegiados ou ECALL/EBREAK.
   Branch não tomado não falha pelo alinhamento de um alvo não utilizado.
5. Sinais commit_* expõem aposentadoria para TB; não são interface oficial de
   pinos. Top de integração é provisório. UART/GPIO do desenho do guia carecem
   de contratos; não adicionar periféricos por suposição.
6. Blocos iniciais são integrados em bancadas progressivas até existir o core.
   Depois todas essas ligações são verificadas no processador. Não contabilizar
   instruções por teste isolado de ALU. Usar tags por marco para rastreabilidade.
7. Não usar uma instrução de sistema fictícia para terminar os testes. Firmware
   próprio escreve uma assinatura na DMEM e permanece em loop; TB detecta a
   assinatura. Testes por instrução observam commit_valid e timeout.
8. Não iniciar o fluxo físico do processador antes de ISA e firmware oficial
   validados, conforme AGENTS.md §33. A instalação e o smoke test do ambiente
   LibreLane são preparação de infraestrutura e não alteram esse marco. Lint
   não equivale a síntese física nem a GDSII.

## Pendências oficiais

Decisão adicional em 2026-10-13: por autorização do usuário, desenvolver o
[CRC provisório CMOS](crc_provisional.md), habilitado por `EXPERIMENTAL_XICRC`.
O perfil padrão e a matriz oficial permanecem 41/47. P01 só se encerra após
confirmação do comportamento pela competição.

Ainda em 2026-10-13: `simple_system` usa ROM 2 KiB/RAM 1 KiB, bases preservadas,
CRC provisório ativo e assinatura em 0x100103f0. Linker separa pilha/dados.
ROM vira constantes e RAM vira registradores na síntese lógica genérica;
nenhuma macro física é presumida. Ver [contrato](../modules/simple_system.md).
O experimento não encerra requisitos do top final nem do firmware oficial.

| ID | Lacuna | Evidência | Impacto |
|---|---|---|---|
| P01 | CRC: papel de rs1/rs2, aplicação da seed, ordem dos bytes e bits altos de rd | Mensagem de 20/10 confirma CCITT-FALSE e tamanhos; PDF pp.12,14–15 não fecha operandos | bloqueia homologação das 3 Xicrc |
| P02 | nomes e comportamento das 3 instruções sistema/sincronização | PDF p.2: apenas quantidade | bloqueia categoria; não presumir nomes pela contagem |
| P03 | arquivo do firmware oficial e critérios de término | Mensagem de 19/10: testes assembly para IMEM, publicação prevista após autorização | bloqueia M9+ |
| P04 | pinos UART/GPIO e interface final de submissão | PDF pp.9–10: figura 12 pinos, tabela apenas clk/rst | top físico pendente |

A especificação RISC-V oficial complementa semântica e codificação das instruções
padronizadas; não resolve decisões exclusivas da competição.

Revisão de 20/10/2026: [esclarecimentos recebidos](clarifications_20261020.md).
Mantemos o RTL e os parâmetros atuais: o algoritmo CRC foi identificado, mas
faltam exemplos/pseudocódigo dos operandos. Não fixar `0xFFFF` em toda instrução
sem confirmar se a inicialização é por mensagem ou por operação. Os programas
próprios já são convertidos em palavras carregadas na IMEM; o oficial não chegou.
