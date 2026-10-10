# Validação do instalador — 2026-10-10

Escopo: dependências de simulação/firmware, reinstalação, atualização e ambiente
físico independente do workspace pai. O RTL não foi alterado.

## Instalação limpa

Cópia temporária do projeto montada em `/project` num contêiner `ubuntu:24.04`,
sem as ferramentas do host. Imagem de base:
`ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55`.
APT executado como root somente nesse contêiner descartável.

Comandos executados sequencialmente:

```bash
bash scripts/setup/install.sh
bash scripts/setup/update.sh
make regression
```

Instalação e atualização: PASS. O instalador também recuperou uma `.venv`
parcial, criada antes de `python3-venv` estar disponível.

| Ferramenta | Versão instalada pelo Ubuntu |
|---|---|
| Python | 3.12.3 |
| Make | 4.3 |
| Git | 2.43.0 |
| Icarus | 12.0 |
| Verilator | 5.020 |
| GCC RISC-V | 13.2.0 |
| Binutils RISC-V | 2.42 |

Regressão: **28/28 testbenches PASS**, lint Verilator PASS. Firmware próprio:
assinatura `600dc0de`, 598 instruções aposentadas, 2579 ciclos. ISA atual:
**41/47 (87,23%)**; firmware oficial permanece pendente.

O [manifesto da regressão](ubuntu-24.04-regression.json) registra os hashes do
RTL, firmware e testes. As evidências desta instalação foram separadas dos
logs existentes para preservar alterações locais do usuário.
O hash de `scripts/openlane/environment.sh` nesse manifesto antecede o ajuste
de acesso ao grupo da imagem; esse ajuste foi validado pelo smoke físico abaixo.

## Diagnóstico e proteções

- `check.py` no host: PASS, incluindo compilação RV32I_Zmmul/ILP32.
- `check.py` com PATH sem ferramentas: erro e lista de executáveis ausentes.
- `update.sh --pull` com checkout alterado: recusa antes de atualizar.
- Opções desconhecidas: saída 2.
- Sintaxe Bash, parsing Python e receitas Make: verificados.

## Ambiente físico

Imagem `isaiassh/unic-cass-tools:1.1.0`, LibreLane 3.0.0rc1, SKY130A.
Somente este repositório foi montado no contêiner.

`make openlane-env-check`: PASS. `make openlane-env-smoke`: PASS, 80 etapas,
GDSII do exemplo, DRC/LVS/antena sem violações reportadas. Resultados físicos
temporários descartados com o contêiner. Não é validação física do processador.
O check e o smoke também passaram com UID/GID `12345:12345` e grupo suplementar
1000, validando o acesso às ferramentas por um usuário diferente do da imagem.

O smoke mantém avisos da imagem/exemplo sobre espaçamento de pinos, células
Liberty duplicadas, nets sem conexão, LEF58, limites de comprimento e ausência
de VSRC. Eles não impediram a conclusão.

Docker precisa estar instalado e acessível no host. Foram validados Ubuntu
24.04 x86_64 e Docker a partir de WSL; outros sistemas não foram validados.
