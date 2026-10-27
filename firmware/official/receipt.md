# Recebimento do firmware oficial — 27/10/2026

Fonte identificada; execução completa no core PASS, com log/VCD identificados. Registro de origem e hashes
em [source.json](source.json). [Contrato extraído do CRC](../../docs/architecture/crc_official_20261027.md).

| Campo | Valor |
|---|---|
| Data / origem | 27/10/2026; repositório fornecido pelo usuário |
| Revisão | edc7d5990d2185942081ee8a6899aa603cc91569 |
| Arquivos | README.md, firmware.s e firmware.txt; hashes em source.json |
| Formato recomendado para validação | firmware.txt: pares de endereço absoluto/palavra em sintaxe de case Verilog |
| Fonte assembly | firmware.s; não é necessário remontar para usar a imagem publicada |
| Entrada / base IMEM | 0x00400000 |
| Tamanho da imagem | 259 palavras / 1036 bytes; último endereço 0x00400408 |
| Código / constantes | 254 palavras de código, seguidas por cinco palavras de constantes |
| Conversão | Preservar cada palavra e endereço; gerar o formato de readmemh da nossa IMEM |
| Dados constantes | Já incluídos na IMEM; também são acessados por loads |
| Área BSS na fonte | test_ram: 16 bytes; dest_data: 12 bytes; conferir endereços durante a integração |
| Contrato CRC | rs1=dados, rs2=CRC anterior, FFFF por software e bytes mais significativos primeiro |
| Instruções de sistema | Não identificadas no código dessa revisão; lacuna de 47/47 continua separada |
| Sucesso / falha | Escrita final de x4=0 / FFFFFFFF, seguida de loop |
| PCs da escrita final na imagem | Sucesso 004003E8; falha 004003F0 |
| Timeout do TB | A definir na integração, sem aceitar o estado de reset como sucesso |
| Execução oficial / logs / waveform | PASS: 252 aposentadorias, 1026 ciclos, 16 CRCs; [rodada identificada](../../results/experiments/crc-official-20261027/README.md) |

## Ordem de integração executada em 27/10

1. Obter os arquivos da revisão registrada e conferir seus hashes.
2. Adequar RTL/modelo/vetores CRC e o firmware próprio ao contrato recebido.
3. Converter firmware.txt para a imagem IMEM completa, incluindo as constantes.
4. Configurar o top de validação com CRC habilitado e capacidades compatíveis.
5. Criar o TB com detecção da escrita de término, timeout e primeira falha;
   não reutilizar a assinatura da DMEM dos programas próprios.
6. Executar a imagem e a regressão, registrar commit/log/waveform/hashes e só
   depois atualizar o resultado oficial e o relatório.

A imagem pode ser usada sem recompilação. Eventual remontagem de firmware.s exige
conferir endereços, seções e equivalência com a imagem publicada antes de substituir
as palavras. A validação funcional e o mock de síntese são usos distintos no README.

O TB confirma x4 no RF após a borda e exige três commits no loop final.
A captura VCD foi reconciliada com o log; a figura está no relatório v0.6.
