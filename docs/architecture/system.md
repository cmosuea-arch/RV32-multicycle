# Contrato CMOS de sistema/sincronização

Decisão de integração de 27/10/2026, baseada na
[revisão normativa](system_audit_20261027.md). A ISA define FENCE, ECALL e EBREAK;
o tratamento descrito abaixo define o ambiente de execução CMOS (EEI), sem
afirmar que seja um protocolo de pinos exigido pela competição.

## FENCE

Opcode `0x0f`, funct3 `000`. O núcleo executa uma instrução por vez, sem cache,
buffer de stores, pedidos pendentes ou handshake externo. O store termina na
borda de MEMORY e o load antes do próximo FETCH. Assim, todos os acessos
anteriores já terminaram ao executar FENCE; o próximo só começa depois dela.
FENCE percorre EXECUTE/WRITEBACK, aposenta com rd=0 e avança PC+4, sem escrever
RF ou memória. Trata todos os campos fm/pred/succ conservadoramente como uma
barreira completa e ignora rs1/rd, conforme permitido para a base RV32I.
FENCE.I (funct3=001) continua fora do perfil, assim como Zicsr.

## ECALL e EBREAK

Somente as palavras exatas `0x00000073` e `0x00100073` são reconhecidas.
EXECUTE transfere para o estado terminal TRAP=6, distinto de FAULT=5.
Essas instruções não aposentam, não avançam o PC nem modificam RF/memória.
Instruções anteriores completam; as posteriores não executam.

Core e top de integração acrescentam estas saídas ao fim da interface:

| Saída | Contrato |
|---|---|
| trap_o | Nível alto enquanto TRAP estiver ativo; não é um pulso de commit |
| trap_ebreak_o | Válido com trap_o: 0=ECALL, 1=EBREAK; zero fora de TRAP |
| trap_pc_o[31:0] | PC da instrução que solicitou o trap; zero fora de TRAP |

O ambiente observa o pedido e encerra esta execução. Não há serviços de sistema,
retorno de trap, CSR, modo privilegiado ou protocolo de debugger implementados.
`trap_ebreak_o` é um discriminador CMOS, não uma codificação de mcause.
TRAP/FAULT permanecem estáveis até reset síncrono; reset cancela efeitos pendentes
e reinicia FETCH em `0x00400000`. O reset também suprime trap_o/oe_o/we_o/commit.
O [manual, introdução](https://docs.riscv.org/reference/isa/v20260120/unpriv/intro.html)
atribui o tratamento ao EEI; um trap solicitado pode encerrar a execução,
sem retomada. Esta é a política escolhida para o ambiente CMOS.

O top `riscv_top` propaga os sinais separados. O `simple_system`, cuja interface
reduzida é mantida, agrega trap e falha na saída fault_o para não deixar o usuário
aguardando uma assinatura que não chegará. Isso não representa sucesso de firmware.
Uma futura memória com latência externa ou buffer exigirá revisar FENCE.

## Verificação e contagem

Decoder: máscaras FENCE, codificações SYSTEM exatas e vizinhas ilegais.
FSM: TRAP terminal, prioridade de reset e separação de FAULT.
Integração: store/FENCE/load, RF preservado, ausência de acesso posterior,
PC/motivo estáveis, zero aposentadorias de ECALL/EBREAK e recuperação por reset.
O firmware oficial publicado exercita 44 tipos; o fechamento das outras três
usa testes próprios. Nenhum trap é contado como aposentadoria.
