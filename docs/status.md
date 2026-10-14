# Estado do projeto — 2026-10-13

Versão parcial de entrega: `rtl-subset-v0.1`. **41/47 instruções (87,23%)**.
Matriz por instrução e categoria: [isa/coverage.md](isa/coverage.md).
Fonte RTL validada: tag `isa-41-v1` (`ea6bccd`); a tag da entrega também inclui
firmware, automação, documentação e evidências finais.

As tags acima identificam a baseline histórica. A versão atual acrescenta CRC
provisório (opt-in) e `simple_system`, conforme evidências em
[`results/experiments/`](../results/experiments/simple/README.md).

| Marco | Estado | Evidência / limite |
|---|---|---|
| M0 — baseline | Parcial | Contratos dos blocos confirmados congelados; CRC/pinagem pendentes |
| M1 — datapath básico | PASS | PC + IMEM + IR e demais blocos básicos integrados |
| M2 — primeira instrução | PASS | ADD/SUB/ADDI, tag core-smoke-v1 |
| M3 — operações básicas | PASS | 21/47, tag isa-21-v1 |
| M4 — controle de fluxo | PASS | 29/47, tag isa-29-v1 |
| M5 — memória | PASS | 37/47, tag isa-37-v1 |
| M6 — Zmmul | PASS | 41/47, tag isa-41-v1 |
| M7/M8 — Xicrc e ISA completa | NOT DONE | Definições oficiais insuficientes para as 6 restantes |
| Firmware próprio | PASS | C/assembly, assinatura 600dc0de; 598 aposentadorias, 2579 ciclos |
| M9 — firmware oficial | NOT DONE | Arquivo/protocolo de validação oficial ausentes |
| M10 — RTL final | NOT DONE | Faltam M7–M9 e interface final |
| M11/M12 — OpenLane/GDSII | Não iniciados | Pré-requisitos AGENTS.md §33 não atendidos |
| Ambiente físico | PASS | LibreLane/OpenROAD/SKY130A e smoke test 80/80 até GDSII |
| CRC experimental | PASS no contrato CMOS | 3 instruções; M7 oficial continua pendente |
| simple_system | PASS em RTL e netlist genérica | ROM 2 KiB/RAM 1 KiB, firmware próprio com CRC; sem fluxo físico |

Blocos ALU, Register File, Immediate, PC, IR, IMEM, Branch Comparator, LSU, DMEM,
Address Decoder e Multiplicador têm RTL, TB unitário, integração, diagrama Mermaid,
documentação, evidências PASS e commits identificados. Decoder, FSM e core estão
funcionais para as 41 instruções. Top de integração executável, top físico pendente.

Verificação atual: **31 testbenches PASS + lint Verilator PASS**, sem diagnósticos
de compilação Icarus. Teste ISA: **76.409 aposentadorias**, 45 stores físicos e
12 bytes finais comparados ao modelo Python. Decoder: 131.072 combinações de
opcode/funct3/funct7. Detalhes em [verification.md](verification.md).

O perfil experimental acrescenta CRCB/CRCH/CRCW às 41 instruções, mas não muda
a cobertura de conformidade: **41/47 (87,23%)**. Polinômio/operandos foram escolhidos
internamente por autorização do usuário; confirmação oficial continua necessária.
O sistema mínimo passou também por síntese lógica e dois boots na netlist.

Pendências para retomar: [architecture/official_questions.md](architecture/official_questions.md).
Os diagramas no ChipInventor, relatório PDF e vídeo da submissão não estão prontos.
**O projeto completo e a parte RTL da competição permanecem NOT DONE.**
