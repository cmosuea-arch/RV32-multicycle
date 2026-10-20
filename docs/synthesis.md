# Síntese lógica do simple_system

Tutorial: [aula 7 — síntese](../labs/rtl-to-gds/07-sintese.md).
Contrato do circuito: [simple_system](modules/simple_system.md).

## Executar

Na raiz do projeto, após preparar as dependências:

```bash
make doctor
make simple-system
make simple-synth
```

`make simple-synth` compila o firmware, sintetiza o RTL com Yosys e simula a
netlist com Icarus/vvp. Não requer Docker ou PDK. Para ver as receitas:

```bash
make -n simple-synth
```

## Entrada e implementação

Top: `rtl/simple_system.sv`, clock de subida e reset síncrono ativo alto.
CRC provisório habilitado, ROM de 2 KiB e RAM de 1 KiB. A imagem `build/simple.hex`
é incorporada na lógica da ROM; a RAM é mapeada em registradores/multiplexadores.
O software inicializa dados/BSS e escreve a assinatura em 0x100103f0.

Yosys recebe apenas os arquivos `rtl/*.sv`. A bancada
`scripts/synth/tb_simple_netlist.sv` entra depois, junto da netlist gerada, para
verificar dois boots por meio de done/success/fault.

## Saídas e critérios

| Arquivo | Uso |
|---|---|
| `build/simple_netlist.v` | circuito sintetizado |
| `build/simple_netlist.json` | estrutura e atributos |
| `results/logs/simple_synth.log` | sequência Yosys e estatísticas |
| `results/logs/simple_netlist.log` | execução do firmware na netlist |
| `results/logs/simple_synth.json` | status, versão Yosys, células e SHA256 |

```bash
cat results/logs/simple_netlist.log
python3 -m json.tool results/logs/simple_synth.json
```

O script exige síntese sem erro, memória mapeada, ausência de init de registradores,
lógica sequencial, saídas não constantes e PASS na simulação da netlist.
Timeout: 180 segundos por processo. O fluxo tem resumo próprio e não atualiza
`results/logs/regression.json` nem a cobertura de ISA.

Na [rodada de referência](../results/experiments/simple/README.md): 32922 células
genéricas com Yosys 0.39+124, firmware de 608 bytes, dois boots aprovados.
Os hashes e a versão da ferramenta delimitam essa evidência.

## Alcance e próximo passo

Não há biblioteca SKY130A, restrições de timing, parasitas, área física, DRC/LVS
ou GDSII nesta síntese genérica. Simular dois boots também não é prova formal
de equivalência para todas as entradas.

O próximo passo experimental é definir configuração LibreLane, clock/restrições,
área e estratégia de memórias, e avaliar o mapeamento físico. Ver
[aula 8 — OpenLane](../labs/rtl-to-gds/08-introducao-openlane.md).
Os arquivos e comandos do próximo experimento já estão
[preparados para execução manual](../openlane/simple_system/README.md), sem
rodada mapeada concluída. O usuário pode estudar `make -n simple-openlane-synth`
antes de executá-lo; esse alvo também recompila e valida a netlist genérica.
Os marcos finais da competição continuam dependentes da ISA, firmware e interface
oficiais, conforme [status](status.md).
