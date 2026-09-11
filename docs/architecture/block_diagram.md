# Baseline v1 — organização

Fonte principal: Block Guide, seções 2–4, páginas físicas 9–23 do PDF combinado.

```mermaid
flowchart LR
 PC --> IMEM
 IMEM --> IR
 IR --> DEC[Decoder e FSM]
 IR --> IMM[Immediate Extension]
 IR --> RF[Register File]
 RF --> ALU
 IMM --> ALU
 PC --> ALU
 RF --> BC[Branch Comparator]
 RF --> MULT[Multiplicador]
 RF -. pendente .-> CRC
 ALU --> RES[Registro de resultado]
 RES --> LSU
 RF --> LSU
 LSU --> AD[Address Decoder]
 AD --> IMEM
 AD --> DMEM
 DMEM --> AD
 IMEM --> AD
 AD --> LSU
 LSU --> WB[Multiplexador writeback]
 RES --> WB
 MULT --> RES
 WB --> RF
 DEC --> PC
```

O desenho é arquitetural: IMEM é acessada por um único barramento via decoder,
tanto no fetch quanto em loads de constantes. Ligações diretas PC/IMEM e IMEM/IR
mostram o fluxo lógico. Diagramas Mermaid são versionados; reprodução no
ChipInventor para a submissão permanece um entregável separado.
