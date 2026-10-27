# Revisão de documentação e comentários — 27/10/2026

Base funcional: `isa-47-v1`, commit `d76fc2c`. Esta revisão acrescenta o
[guia de leitura](../../../docs/code_guide.md), atualiza aulas/contratos e explica
os blocos nos comentários, preservando a lógica e as receitas de execução.
A tag funcional e as evidências anteriores permanecem nos respectivos commits.

## Conferências

| Verificação | Resultado / evidência |
|---|---|
| Código comentado | 35 arquivos: AST Python idêntica; tokens RTL/TB/C/assembly/linker idênticos sem comentários; alvos/receitas Make preservados |
| Comparação editorial | [Antes/depois e hashes](comments-check.json), contra `d76fc2c` |
| Receitas Make | 12 prévias `make -n`, incluindo síntese/OpenLane, idênticas à base; os comandos físicos não foram executados |
| Sintaxe shell | Scripts existentes conferidos com `bash -n`, sem instalação ou Docker |
| Regressão em cópia temporária | [33 TBs e lint PASS](regression.log), incluindo o firmware oficial |
| ISA / sistema | 88.794 aposentadorias no trace, 512 FENCE e 256 traps de cada tipo; [manifesto sistema](system.json) |
| Imagem oficial | 252 aposentadorias, 1026 ciclos, 16 CRCs e 44 tipos; [manifesto](official_firmware.json) |
| Testes da automação | [Sete de cobertura](coverage-tests.log) e [cinco do conversor](official-image-tests.log), todos PASS |
| Identificação | [94 hashes da regressão](regression.json) correspondem às fontes desta revisão; [resumo da conferência](validation.json) |

Os builds/logs locais da prática e a matriz publicada não foram sobrescritos.
A matriz continua identificando o marco funcional `isa-47-v1`; esta pasta registra
a regressão complementar das fontes com comentários atualizados. As mesmas
contagens não significam que os hashes antigos coincidam com arquivos editados.

Não houve síntese, execução física, captura VCD nova ou alteração do PDF técnico.
O relatório v0.7 e suas figuras continuam descrevendo a implementação preservada.
Os [resultados físicos e entregáveis pendentes](../../../docs/status.md) permanecem
fora do alcance desta revisão editorial.

Para conferir a sua cópia: `make regression`. Esse comando recompõe as entradas,
simula e publica hashes novos em `results/logs/`; não altera esta pasta arquivada.
