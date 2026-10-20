# Firmware oficial — PENDENTE

O PDF p.4 informa distribuição na plataforma ChampionCHIP. Nenhum arquivo
oficial está presente neste repositório. Não atribuir PASS ao firmware oficial
com base no demo próprio. Quando disponível, conferir mapa, inicialização de
memórias e protocolo de término antes de integrar o testbench.

Atualização de **20/10/2026**: segundo mensagem de 19/10 encaminhada pelo usuário,
será um programa assembly de testes de todas as instruções, a ser convertido
em código de máquina para a IMEM. A publicação depende de autorização; não há
data nem formato de arquivo confirmados. A equipe pode usar programas próprios
até o recebimento, sem substituir a validação oficial.

O caminho próprio já existe: fonte → GCC/assembler/linker → ELF → binário →
`build/smoke.hex` → `$readmemh` da IMEM. `programs.py` também gera diretamente
palavras para `build/isa.hex`, verificadas por trace no TB. Ao receber o oficial,
conferir se vem como fonte, ELF ou imagem, a ordem/quantidade de palavras, ponto
de entrada, memória de dados e critério de sucesso antes de adaptar esse caminho.
Detalhes: [registro dos esclarecimentos](../../docs/architecture/clarifications_20261020.md).

Quando os arquivos chegarem, preencher o [checklist de recebimento](receipt.md)
antes de adaptar o carregamento da IMEM e o testbench. Ele não pressupõe formato
de imagem, instruções de término ou assinatura do programa oficial.
