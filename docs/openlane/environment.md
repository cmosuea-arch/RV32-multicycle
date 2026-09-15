# Ambiente LibreLane/OpenLane

## Estado

O ambiente físico está instalado e validado no WSL2 por meio da imagem Docker
`isaiassh/unic-cass-tools:1.1.0` usada pelo repositório UNIC-CASS. LibreLane é o
sucessor do OpenLane 2 e fornece o fluxo RTL até GDSII deste projeto.

Versões verificadas em 2026-09-15:

| Componente | Versão / identificação |
|---|---|
| LibreLane | `3.0.0rc1` |
| OpenROAD | `v2.0-25787-gee9759486` |
| Yosys da imagem | `0.44` |
| PDK | `sky130A` |
| PDK Volare | `0fe599b2afb6708d281543108caf8310912f54af` |

O verificador encontrou também Icarus Verilog, Verilator, Magic, Netgen,
KLayout, ngspice, xschem, OpenVAF, CACE e CVC-RV.

## Uso

Com Docker Desktop aberto e a integração desta distribuição WSL habilitada:

```sh
make openlane-env-check
make openlane-env-smoke
make openlane-shell
```

`openlane-env-check` confirma ferramentas e PDKs. `openlane-env-smoke` executa
o projeto de teste embutido até GDSII em um diretório temporário. O shell abre
o contêiner com este repositório em
`/home/designer/shared/cmos-riscv` e com `PDK_ROOT=/opt/pdks`.

Dentro do contêiner, o wrapper padrão é:

```sh
/home/designer/shared/bin/librelane-local <config.yaml>
```

A imagem é fixada pelo script para preservar a reprodução. Para testar outra
imagem sem editar o repositório, defina `UNICCASS_DOCKER_IMAGE`.

## Validação realizada

O smoke test de infraestrutura percorreu 80/80 etapas em 59 segundos, gerou
GDSII e terminou com DRC, LVS e antena aprovados. Os avisos observados estão
registrados em `results/openlane/environment-smoke.md`.

Essa validação comprova o ambiente. O fluxo físico do `riscv_top` continua
aguardando ISA completa, firmware oficial, definição da interface física e uma
estratégia sintetizável para IMEM/DMEM, conforme `AGENTS.md`.
