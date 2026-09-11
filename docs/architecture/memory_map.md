# Mapa de memória v1

Fonte: Block Guide §4, páginas físicas 20–23.

| Região | Base | Limite inclusivo da referência | Capacidade |
|---|---|---|---|
| IMEM | 0x00400000 | 0x007fffff | 4 MiB |
| DMEM | 0x10010000 | 0x10011fff | 8 KiB |

Endereçamento externo em bytes, little-endian (exemplos do guia). Índice interno
de palavra = (endereço − base) >> 2. LSU usa os dois bits baixos antes de o
decoder alinhar o endereço. IMEM permite loads de constantes e nunca escrita.
DMEM permite escrita independente de cada byte com bw[0] para bits [7:0].

Tamanhos parametrizáveis, padrão IMEM_WORDS=1048576 e DMEM_WORDS=2048.
Testbenches usam ROM menor, explicitamente parametrizada, para rapidez.
O decoder verifica a capacidade configurada, sem alias fora da faixa.
Reset não apaga DMEM; software deve inicializar .data/.bss antes de lê-las.
ROM tem INIT_FILE opcional (hex, uma palavra por linha); posições restantes
contêm 0, uma codificação não suportada que produz FAULT no núcleo.
