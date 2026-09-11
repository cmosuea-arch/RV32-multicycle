# AGENTS.md — CMOS RISC-V RTL

## 1. Objetivo deste arquivo

Este arquivo define a rota operacional para desenvolvimento, verificação e integração da parte RTL do processador RISC-V da CMOS para a Fase 2 da ChampionCHIP.

A regra principal é:

> **Atacar um bloco por vez até ele estar completamente especificado, implementado, testado, documentado e integrado antes de avançar para o próximo.**

O processador deve crescer de forma incremental, mantendo regressão contínua e evitando uma integração “big bang” no final.

---

## 2. Fontes de verdade

A ordem de prioridade para decisões técnicas é:

1. **ChampionCHIP — Block Guide oficial**
   - Define a arquitetura de referência.
   - Define os blocos obrigatórios.
   - Define o comportamento esperado do processador.
   - Define interfaces, mapa de memória e organização multiciclo.

2. **ChampionCHIP — Guia de Submissão da Fase 2**
   - Define os entregáveis.
   - Define a cobertura exigida da ISA.
   - Define testbenches, datapath, firmware demo, OpenLane, GDSII, relatório e vídeo.

3. **Especificação oficial RISC-V**
   - Usar para conferir semântica de instruções, campos, imediatos e comportamento arquitetural.

4. **Ibex oficial isolado**
   - Usar apenas como **referência técnica auxiliar**.
   - Não usar como arquitetura-base do projeto.
   - Não copiar diretamente pipeline, controle, fetch, debug, CSRs, PMP ou interfaces externas sem necessidade.

5. **Decisões internas CMOS**
   - Devem ser registradas em documentação própria quando o material oficial deixar liberdade de implementação.

### Regra

Se houver conflito entre Ibex e ChampionCHIP, **ChampionCHIP vence**.

---

## 3. Arquitetura-alvo

A arquitetura de referência da ChampionCHIP é um processador:

- RISC-V de 32 bits;
- multiciclo;
- baseado em RV32I;
- com extensão Zmmul;
- com extensão customizada Xicrc;
- com execução organizada em estados equivalentes a:
  - Fetch;
  - Decode;
  - Execute;
  - Write Back.

Blocos principais:

- ALU;
- Register File;
- Program Counter;
- Instruction Register;
- Immediate Extension;
- Branch Comparator;
- Multiplicador;
- CRC;
- LSU;
- Control Unit / FSM;
- IMEM;
- DMEM;
- Address Decoder;
- Top-level.

---

## 4. Estratégia global

A implementação deve seguir esta ordem:

```text
BASELINE ARQUITETURAL
        ↓
ALU
        ↓
REGISTER FILE
        ↓
IMMEDIATE EXTENSION
        ↓
PROGRAM COUNTER
        ↓
INSTRUCTION REGISTER
        ↓
IMEM
        ↓
FSM MÍNIMA
        ↓
ARITHMETIC REGISTER
        ↓
ARITHMETIC IMMEDIATE
        ↓
UPPER IMMEDIATE
        ↓
BRANCH COMPARATOR
        ↓
BRANCH
        ↓
JUMP
        ↓
LSU
        ↓
DMEM
        ↓
ADDRESS DECODER
        ↓
LOAD / STORE
        ↓
MULTIPLICADOR
        ↓
CRC
        ↓
SISTEMA / SINCRONIZAÇÃO
        ↓
TOP-LEVEL
        ↓
47 / 47
        ↓
FIRMWARE OFICIAL
        ↓
OPENLANE
        ↓
GDSII
```

---

# 5. Fase 0 — Baseline arquitetural

Antes do primeiro RTL, congelar a primeira versão dos contratos entre os blocos.

## 5.1 Definir

- largura de todos os barramentos;
- convenção de nomes;
- política de reset;
- polaridade do reset;
- comportamento do clock;
- interface da ALU;
- interface do Register File;
- interface do PC;
- interface do IR;
- interface da extensão de imediatos;
- interface do comparador de branch;
- interface da LSU;
- interface da IMEM;
- interface da DMEM;
- interface do Address Decoder;
- sinais principais da FSM;
- sinais de write enable;
- sinais de output enable;
- byte write;
- seleção de writeback;
- seleção de operandos;
- mapa de memória.

## 5.2 Mapa de memória de referência

- IMEM: base `0x00400000`
- DMEM: base `0x10010000`

Não alterar sem decisão arquitetural explícita.

## 5.3 Saída da fase

Criar:

```text
docs/architecture/
├── block_diagram.md
├── interfaces.md
├── memory_map.md
└── decisions.md
```

---

# 6. Critério universal de conclusão de bloco

Um bloco NÃO está concluído quando apenas compila.

Um bloco só pode receber status `DONE` quando atender todos os itens:

```text
[ ] especificação entendida
[ ] interface definida
[ ] RTL implementado
[ ] compilação limpa
[ ] testbench autoverificável
[ ] casos normais testados
[ ] casos de borda testados
[ ] todos os testes PASS
[ ] diagrama do módulo criado
[ ] documentação curta atualizada
[ ] commit identificado
[ ] integração realizada
[ ] regressão anterior continua PASS
```

Se qualquer item falhar:

```text
status = NOT DONE
```

---

# 7. Bloco 1 — ALU

## 7.1 Objetivo

Implementar a unidade aritmética e lógica usada pelo datapath.

Operações do guia:

- PASS_B
- ADD
- SUB
- AND
- OR
- XOR
- SLL
- SRL
- SRA
- SLT
- SLTU

## 7.2 Verificação mínima

Testar:

- zero;
- valores positivos;
- valores negativos;
- overflow aritmético natural de 32 bits;
- shift 0;
- shift 31;
- signed vs unsigned;
- comparações iguais;
- comparações limite;
- padrões `0x00000000`;
- `0xFFFFFFFF`;
- `0x80000000`;
- `0x7FFFFFFF`.

## 7.3 Uso do Ibex

Pode consultar:

- implementação das operações;
- tratamento signed/unsigned;
- lógica de shift;
- comparações.

Não copiar interface sem necessidade.

---

# 8. Bloco 2 — Register File

## 8.1 Requisitos

- 32 registradores de 32 bits;
- `x0` fixo em zero;
- duas leituras;
- uma escrita;
- escrita sincronizada;
- leitura conforme arquitetura definida pela CMOS.

## 8.2 Verificação

Testar:

- escrita em x1–x31;
- leitura simultânea;
- tentativa de escrita em x0;
- leitura de x0;
- escrita/leitura consecutiva;
- reset, se aplicável.

## 8.3 Uso do Ibex

Consultar apenas:

- comportamento de x0;
- organização de leitura/escrita;
- corner cases.

---

# 9. Bloco 3 — Immediate Extension

## 9.1 Formatos

Validar imediatos:

- I;
- S;
- B;
- U;
- J.

## 9.2 Verificação

Para cada formato:

- imediato positivo;
- imediato negativo;
- menor valor;
- maior valor;
- reconstrução dos bits;
- extensão de sinal.

## 9.3 Uso do Ibex

O decoder do Ibex pode ser usado como referência de montagem dos formatos.

A implementação final deve seguir a arquitetura CMOS.

---

# 10. Bloco 4 — Program Counter

## 10.1 Funções

- manter endereço atual;
- PC + 4;
- carregar endereço de branch;
- carregar endereço de jump;
- resetar para endereço inicial definido.

## 10.2 Testes

- sequência normal;
- reset;
- branch tomado;
- branch não tomado;
- jump;
- alvos para frente;
- alvos para trás.

---

# 11. Bloco 5 — Instruction Register

## 11.1 Função

Capturar a instrução recebida da IMEM no ciclo de Fetch.

## 11.2 Testes

- captura com enable;
- retenção sem enable;
- sequência de instruções;
- reset, se aplicável.

---

# 12. Bloco 6 — IMEM

## 12.1 Função

Fornecer as instruções executadas pelo processador.

## 12.2 Testes

- leitura no endereço base;
- leitura sequencial;
- alinhamento de 4 bytes;
- leitura de diferentes posições;
- conteúdo conhecido por testbench.

## 12.3 Primeiro milestone arquitetural

Após:

```text
PC + IMEM + IR
```

validar:

```text
PC = BASE
PC = BASE + 4
PC = BASE + 8
PC = BASE + 12
...
```

e confirmar que a instrução correta chega ao IR.

---

# 13. Bloco 7 — FSM mínima

Não iniciar a FSM completa antes dos blocos básicos existirem.

## 13.1 Primeira versão

Implementar inicialmente:

```text
RESET
  ↓
FETCH
  ↓
DECODE
  ↓
EXEC_ALU
  ↓
WRITEBACK
  ↓
FETCH
```

## 13.2 Primeiro objetivo

Executar um programa mínimo contendo operações simples de ALU.

O primeiro milestone real do processador é:

> **buscar, decodificar, executar e escrever o resultado de uma instrução corretamente.**

---

# 14. Primeira cobertura funcional da ISA

Após ALU + Register File + Immediate + PC + IR + IMEM + FSM mínima:

## 14.1 Arithmetic and Logic — Register

Meta:

```text
10 / 10
```

## 14.2 Arithmetic and Logic — Immediate

Meta:

```text
9 / 9
```

## 14.3 Upper Immediate

Meta:

```text
2 / 2
```

Acumulado esperado:

```text
21 / 47
```

Não avançar apenas por contagem.

Cada instrução deve possuir:

- teste individual;
- teste integrado;
- regressão;
- evidência;
- commit.

---

# 15. Bloco 8 — Branch Comparator

## 15.1 Objetivo

Comparar `rs1` e `rs2` conforme a condição de branch.

Cobrir comparações:

- igualdade;
- desigualdade;
- menor que signed;
- maior/igual signed;
- menor que unsigned;
- maior/igual unsigned.

## 15.2 Testes

Incluir:

- iguais;
- positivo vs positivo;
- negativo vs negativo;
- negativo vs positivo;
- signed vs unsigned;
- limites de 32 bits.

---

# 16. Branch e Jump

Após o comparador:

## 16.1 Branch

Meta:

```text
6 / 6
```

Testar cada instrução em dois cenários:

```text
branch_taken = 1
branch_taken = 0
```

## 16.2 Jump

Meta:

```text
2 / 2
```

Testar:

- cálculo do alvo;
- atualização do PC;
- valor escrito em `rd`;
- offsets positivos;
- offsets negativos.

Acumulado esperado:

```text
29 / 47
```

---

# 17. Bloco 9 — LSU

A LSU deve ser tratada como um bloco crítico.

## 17.1 Loads

Cobrir:

- LB;
- LH;
- LW;
- LBU;
- LHU.

Requisitos:

- byte;
- halfword;
- word;
- extensão de sinal;
- extensão de zeros;
- seleção pelos bits inferiores do endereço;
- posicionamento correto.

## 17.2 Stores

Cobrir:

- SB;
- SH;
- SW.

Requisitos:

- posicionamento do dado;
- geração de byte write;
- escrita parcial da palavra.

## 17.3 Testes mínimos

```text
LB  offsets 0,1,2,3
LBU offsets 0,1,2,3
LH  offsets válidos
LHU offsets válidos
LW  alinhado

SB  offsets 0,1,2,3
SH  offsets válidos
SW  alinhado
```

Também testar:

- valores com MSB = 1;
- valores com MSB = 0;
- sign extension;
- zero extension.

## 17.4 Uso do Ibex

Ibex é particularmente útil aqui como referência para:

- byte enable;
- alinhamento;
- máscaras;
- sign extension;
- zero extension;
- organização de loads/stores.

Não copiar a interface de memória do Ibex.

---

# 18. Bloco 10 — DMEM

## 18.1 Função

Memória de dados usada pelas instruções de load/store.

## 18.2 Testes

- leitura;
- escrita;
- escrita por byte;
- escrita por halfword;
- escrita por word;
- conteúdo preservado em bytes não selecionados;
- acesso sequencial.

---

# 19. Bloco 11 — Address Decoder

## 19.1 Função

Selecionar o destino da operação conforme endereço.

Referência:

```text
IMEM → 0x00400000
DMEM → 0x10010000
```

## 19.2 Validar

- seleção correta do dispositivo;
- roteamento de endereço;
- roteamento de `oe`;
- roteamento de `we`;
- roteamento de `bw`;
- retorno de dados;
- IMEM não recebe escrita.

---

# 20. Fechamento de Load/Store

Após:

```text
LSU + DMEM + Address Decoder
```

validar no processador integrado:

```text
Load  = 5 / 5
Store = 3 / 3
```

Acumulado esperado:

```text
37 / 47
```

---

# 21. Bloco 12 — Multiplicador

## 21.1 Extensão Zmmul

Cobrir:

- MUL;
- MULH;
- MULHSU;
- MULHU.

## 21.2 Verificação

Testar combinações:

- signed × signed;
- signed × unsigned;
- unsigned × unsigned;
- zero;
- um;
- -1;
- limites;
- parte alta;
- parte baixa.

## 21.3 Integração

Após TB isolado:

```text
RTL
 ↓
decode
 ↓
datapath
 ↓
FSM
 ↓
writeback
 ↓
regressão completa
```

Meta:

```text
4 / 4
```

Acumulado:

```text
41 / 47
```

---

# 22. Bloco 13 — CRC

## 22.1 Extensão Xicrc

Cobrir as três instruções definidas oficialmente pela ChampionCHIP.

Meta:

```text
3 / 3
```

## 22.2 Processo

```text
TB isolado
 ↓
integração datapath
 ↓
decode
 ↓
controle
 ↓
writeback
 ↓
regressão
```

Acumulado:

```text
44 / 47
```

---

# 23. Sistema / Sincronização

Meta:

```text
3 / 3
```

Usar exclusivamente:

- nomes oficiais;
- codificações oficiais;
- comportamento oficial.

Não preencher lacunas por suposição.

Após esta etapa:

```text
47 / 47
```

---

# 24. Matriz obrigatória por instrução

Manter uma planilha ou arquivo rastreável com:

| Campo | Conteúdo |
|---|---|
| Categoria | grupo oficial |
| Instrução | nome oficial |
| Opcode | oficial |
| Funct3 | quando aplicável |
| Funct7 | quando aplicável |
| Módulo principal | RTL responsável |
| Teste unitário | PASS/FAIL |
| Teste integrado | PASS/FAIL |
| Regressão | PASS/FAIL |
| Firmware | PASS/FAIL |
| Commit | hash/tag |
| Evidência | waveform/log |
| Observação | erro, limitação ou nota |

Mostrar sempre:

```text
implementadas / 47
```

e cobertura percentual total e por categoria.

---

# 25. Regressão contínua

A partir do primeiro bloco integrado, todo novo commit funcional deve preservar os testes anteriores.

Exemplo:

```text
ALU                  PASS
Register File        PASS
Immediate            PASS
PC                   PASS
IR                   PASS
IMEM                 PASS
R-type               PASS
I-type               PASS
```

Após adicionar branch:

```text
TODOS ANTERIORES     PASS
Branch Comparator    PASS
Branch               PASS
Jump                 PASS
```

Após adicionar memória:

```text
TODOS ANTERIORES     PASS
LSU                  PASS
DMEM                 PASS
Address Decoder      PASS
Load                 PASS
Store                PASS
```

Nunca aceitar:

> “o bloco novo funciona, mas quebrou três testes antigos”.

Isso é regressão falha.

---

# 26. Uso correto do Ibex

O Ibex deve permanecer isolado do RTL oficial da CMOS.

Estrutura sugerida:

```text
cmos-riscv/
├── rtl/
├── tb/
├── firmware/
├── docs/
├── scripts/
├── results/
└── external/
    └── ibex/
```

Preferencialmente:

```text
external/ibex
```

como submodule ou clone de referência.

## 26.1 Consultar Ibex para

- ALU;
- Register File;
- Immediate Decode;
- Branch Compare;
- Load/Store;
- semântica de instruções;
- corner cases;
- ideias de verificação.

## 26.2 Não usar Ibex como modelo direto para

- pipeline;
- Control Unit;
- Fetch;
- stalls;
- flush;
- CSRs;
- debug;
- PMP;
- exceções complexas;
- interface de memória;
- top-level.

A FSM da CMOS deve refletir a arquitetura multiciclo exigida pela ChampionCHIP.

---

# 27. Organização do repositório

Estrutura recomendada:

```text
cmos-riscv/
├── AGENTS.md
├── README.md
├── rtl/
│   ├── alu.sv
│   ├── regfile.sv
│   ├── imm_ext.sv
│   ├── pc.sv
│   ├── ir.sv
│   ├── branch_comp.sv
│   ├── lsu.sv
│   ├── multiplier.sv
│   ├── crc.sv
│   ├── control_unit.sv
│   ├── imem.sv
│   ├── dmem.sv
│   ├── address_decoder.sv
│   └── riscv_top.sv
│
├── tb/
│   ├── unit/
│   ├── integration/
│   └── regression/
│
├── firmware/
│   ├── smoke/
│   └── official/
│
├── docs/
│   ├── architecture/
│   ├── modules/
│   ├── isa/
│   └── decisions/
│
├── scripts/
│   ├── sim/
│   └── regression/
│
├── results/
│   ├── waveforms/
│   ├── logs/
│   ├── openlane/
│   └── gds/
│
└── external/
    └── ibex/
```

---

# 28. Regra para commits

Cada commit relevante deve responder:

```text
O que mudou?
Qual bloco?
Qual requisito?
Qual teste prova?
Que regressão foi executada?
```

Exemplos:

```text
feat(alu): implement ADD SUB AND OR XOR
test(alu): add signed and unsigned corner cases
feat(regfile): implement 32x32 register file with x0 hardwired
fix(lsu): correct LBU byte selection for address offset 2
test(regression): validate 29/47 instructions
```

---

# 29. Documentação por bloco

Cada módulo deve possuir:

```text
docs/modules/<modulo>.md
```

Conteúdo mínimo:

```text
# Nome do módulo

## Objetivo
## Entradas
## Saídas
## Comportamento
## Dependências
## Casos especiais
## Testbench
## Casos testados
## Resultado
## Integração
## Commit validado
## Pendências
```

---

# 30. Milestones

## M0 — Baseline

```text
Arquitetura + interfaces + mapa de memória definidos
```

## M1 — Datapath básico

```text
ALU
Register File
Immediate
PC
IR
IMEM
```

## M2 — Primeira instrução executada

```text
Fetch → Decode → Execute → Writeback
```

## M3 — Operações básicas completas

```text
21 / 47
```

## M4 — Controle de fluxo completo

```text
29 / 47
```

## M5 — Memória completa

```text
37 / 47
```

## M6 — Zmmul

```text
41 / 47
```

## M7 — Xicrc

```text
44 / 47
```

## M8 — ISA completa

```text
47 / 47
```

## M9 — Firmware oficial

```text
execução completa sem erros
```

## M10 — RTL congelado

```text
regressão completa PASS
```

## M11 — OpenLane

```text
fluxo físico válido
```

## M12 — GDSII

```text
GDSII gerado e versionado
```

---

# 31. Smoke tests

Antes de regressões longas, manter testes rápidos.

## Smoke 1

```text
ADD
SUB
ADDI
```

## Smoke 2

```text
branch simples
jump simples
```

## Smoke 3

```text
store
load
```

## Smoke 4

```text
MUL
CRC
```

Objetivo:

```text
detectar quebra estrutural em segundos
```

---

# 32. Firmware

Após a ISA estar funcional:

1. executar firmware mínimo próprio;
2. executar smoke firmware;
3. executar firmware oficial da ChampionCHIP;
4. registrar ponto de falha;
5. capturar waveform;
6. identificar instrução;
7. identificar módulo;
8. corrigir;
9. executar regressão;
10. repetir.

Meta final:

```text
Firmware oficial = 100%
```

---

# 33. OpenLane

OpenLane só entra depois que:

```text
RTL funcional
+
regressão PASS
+
firmware validado
```

Cada run deve registrar:

- data;
- responsável;
- commit RTL;
- configuração;
- warnings;
- erros;
- área;
- densidade;
- etapa alcançada;
- GDSII gerado ou não;
- ação seguinte.

---

# 34. Definition of Done da parte RTL

A parte RTL somente pode ser considerada concluída quando:

```text
[ ] todos os módulos possuem RTL
[ ] todos os módulos possuem TB
[ ] todos os módulos possuem documentação
[ ] todos os módulos possuem evidência
[ ] todos os módulos foram integrados
[ ] datapath está versionado
[ ] FSM está versionada
[ ] interfaces estão versionadas
[ ] mapa de memória está versionado
[ ] 47/47 instruções passam
[ ] regressão completa passa
[ ] firmware oficial executa até o final
[ ] versão RTL final possui tag
```

Tag sugerida:

```text
rtl-v1.0-championchip
```

---

# 35. Regra de trabalho para agentes e colaboradores

Ao receber uma tarefa RTL:

1. identificar o bloco;
2. localizar a especificação oficial correspondente;
3. verificar dependências;
4. consultar Ibex apenas se útil;
5. não alterar interfaces sem justificativa;
6. implementar a menor mudança necessária;
7. criar/atualizar TB;
8. executar teste unitário;
9. executar integração;
10. executar regressão;
11. documentar;
12. registrar commit;
13. atualizar cobertura;
14. só então marcar como concluído.

Nunca:

- implementar vários blocos ao mesmo tempo sem necessidade;
- alterar arquitetura silenciosamente;
- aceitar waveform visual como único critério de teste;
- copiar arquitetura do Ibex para substituir a especificação ChampionCHIP;
- avançar com regressão quebrada;
- assumir codificação de instrução não confirmada;
- deixar documentação para o final.

---

# 36. Prioridade operacional

Sempre priorizar nesta ordem:

```text
1. CORREÇÃO FUNCIONAL
2. VERIFICAÇÃO
3. INTEGRAÇÃO
4. REGRESSÃO
5. DOCUMENTAÇÃO
6. FIRMWARE
7. FLUXO FÍSICO
8. OTIMIZAÇÃO
```

Não otimizar área, timing ou estilo antes de existir uma versão funcional e verificável.

---

# 37. Resultado esperado

Ao seguir este AGENTS.md, o processador não deve surgir como um conjunto de módulos isolados.

Ele deve evoluir assim:

```text
bloco correto
      ↓
bloco integrado
      ↓
nova família de instruções
      ↓
regressão preservada
      ↓
processador progressivamente mais completo
      ↓
47 / 47
      ↓
firmware oficial
      ↓
OpenLane
      ↓
GDSII
```

Esse é o caminho principal da frente RTL da CMOS.
