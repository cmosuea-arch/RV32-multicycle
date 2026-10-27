# Revisão de sistema/sincronização — 27/10/2026

## Fontes e identificação

A revisão corrige a pendência anterior de nomes/códigos desconhecidos:

1. O Guia de Submissão, página física 2 do PDF combinado, exige três instruções
   de sistema/sincronização, sem listar seus nomes.
2. O Block Guide, §1.2 (p.7), referencia o manual RISC-V Volume I (2026).
   Os §§2.1 e 2.4 (pp.9 e 11) exigem a base RV32I, além de Zmmul e Xicrc.
3. O [manual RV32I v2.1](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html),
   já relacionado em [sources.md](sources.md), define FENCE (§1.1.7), ECALL
   e EBREAK (§1.1.8). Suas codificações constam em
   [riscv-opcodes/rv_i](https://github.com/riscv/riscv-opcodes/blob/master/extensions/rv_i).
   Ambas as fontes foram conferidas novamente nesta data.

Essa correspondência decorre da exigência de RV32I e da especificação que o guia
referencia; não é uma enumeração explícita da organização. A contagem é coerente:
40 RV32I + 4 Zmmul + 3 Xicrc = 47. FENCE.I pertence a Zifencei e não substitui
uma dessas três instruções.

| Instrução | Codificação | Comportamento especificado |
|---|---|---|
| FENCE | opcode `0001111`, funct3 `000`; exemplo `0x0ff0000f` para `fence iorw,iorw` | Ordenar acessos anteriores e posteriores conforme os campos pred/succ |
| ECALL | `0x00000073` | Solicitar serviço ao ambiente de execução por trap preciso |
| EBREAK | `0x00100073` | Transferir controle ao ambiente de depuração por trap preciso |

FENCE não possui uma única palavra fixa: há campos fm/pred/succ. O manual admite
implementações simples que preservem a ordenação sem uma operação adicional;
isso precisa ser demonstrado para o sistema integrado. ECALL/EBREAK não podem
ser tratados simplesmente como NOPs.

## Situação no momento da revisão (antes da implementação)

O [teste atual de falhas](../../tb/integration/tb_core_faults.sv) injeta
`0x00000073`, `0x00100073` e `0x0000000f` e exige FAULT sem aposentadoria.
Portanto, o RTL atual ainda não implementa essas instruções como operações legais.
O FAULT diagnóstico existente não comprova suporte aos traps de ECALL/EBREAK.

Falta definir e registrar como o ambiente CMOS recebe esses traps (sinalização,
PC/causa, parada ou tratamento), implementar o contrato e verificar os efeitos
arquiteturais. O guia local não especifica um protocolo próprio para isso.
Qualquer exigência adicional da competição deverá ser confirmada com a organização.
Essa questão de integração não impede usar os nomes/códigos oficiais já disponíveis.

O firmware publicado exercita 44 tipos e não fornece teste dessas três instruções.
Serão necessários testes próprios, atualização do decoder/controle e regressão.
Os campos PENDENTE_1/2/3 da matriz atual permanecem como registro da rodada anterior;
a identificação nesta revisão não aumenta a cobertura funcional.

**Resultado desta revisão: 44/47 mantidas; FENCE, ECALL e EBREAK identificadas
pela referência normativa; implementação e validação pendentes.** Nenhum RTL,
testbench ou resultado de síntese foi alterado ou produzido nesta revisão.

## Implementação posterior

Após autorização do usuário, o [contrato EEI CMOS](system.md) foi implementado
e verificado: [47/47, 33 TBs/lint e firmware oficial PASS](../../results/experiments/isa-47-20261027/README.md).
As conclusões de 44/47 acima descrevem o estado anterior à implementação.
