# Validação do ambiente LibreLane

| Campo | Valor |
|---|---|
| Data | 2026-09-15 |
| Responsável | execução automatizada Codex |
| Commit RTL | `63db935` |
| Imagem | `isaiassh/unic-cass-tools:1.1.0` |
| PDK | `sky130A` |
| Configuração | smoke test embutido do LibreLane |
| Etapa alcançada | Classic 80/80 — Report Manufacturability |
| Tempo informado | 59 s |
| GDSII | gerado no diretório temporário do teste |
| DRC | PASS |
| LVS | PASS — circuitos correspondem unicamente |
| Antena | PASS |
| Setup/hold | nenhuma violação |

Comando reproduzível:

```sh
make openlane-env-smoke
```

Avisos finais sem falha do teste:

- distância mínima de pinos ajustada automaticamente para evitar sobreposição;
- mensagens repetidas de biblioteca Liberty;
- duas redes flutuantes no projeto de smoke test;
- regras `LEF58_ENCLOSURE` sem `CUTCLASS` ignoradas pelo roteador;
- limite de comprimento de fio não configurado;
- análise de IR drop indicativa por ausência de `VSRC_LOC_FILES`.

Resultado final emitido pelo LibreLane: `Smoke test passed.`
