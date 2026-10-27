# Confirmação do contrato CRC — fonte recebida em 27/10/2026

O formulário aberto em 20/10 foi respondido pelo uso das instruções no firmware
oficial. O [contrato foi implementado](crc.md), com
[regressão e firmware oficial PASS](../../results/experiments/crc-official-20261027/README.md).
[Análise inicial e limites](crc_official_20261027.md).

## Origem

| Campo | Registro |
|---|---|
| Data da consulta | 27/10/2026 |
| Fonte | [Repositório oficial de firmware da Fase 2](https://github.com/championchip-experience-community/CCX_Brasil_Edition_Firmware_Stage_2) |
| Revisão | edc7d5990d2185942081ee8a6899aa603cc91569 |
| Trecho principal | firmware.s, linhas 279–340; codificações nas linhas 3–13 |
| Identificação dos arquivos | [source.json](../../firmware/official/source.json), com URLs e SHA-256 |

## Respostas extraídas

| Item | Resposta |
|---|---|
| Nomes / tamanhos | CRCB: 8 bits; CRCH: 16; CRCW: 32; CRC de 16 bits |
| Variante | CCITT-FALSE, conforme comunicação de 20/10 e referência de 27/10 |
| Codificação | opcode 0x33; funct7 0x40; funct3 0/1/2 |
| rs1 | Dados |
| rs2 | Acumulador CRC anterior |
| Inicialização | Software fornece FFFF, depois encadeia o resultado em rs2 |
| Ordem dos bytes de dados | Mais significativo selecionado primeiro |
| Resultado comparado | Igualdade de 32 bits com 00001E82; manter extensão com zeros do CRC16 |

O teste oficial processa a mensagem 12 34 56 78 90 AB CD EF como oito bytes,
quatro meias palavras ou duas palavras. Todos os caminhos exigem 1E82.
Os exemplos do formulário anterior usavam o contrato CMOS inverso e não devem
ser adotados como vetores oficiais.

## Checklist de adequação — executado em 27/10

- [x] Identificar a origem, a revisão e os casos de referência.
- [x] Comparar o contrato com o modelo atual e registrar as duas diferenças.
- [x] Atualizar RTL e modelo independente para dados em rs1 e acumulador em rs2.
- [x] Corrigir ordem dos bytes, vetores, modelo arquitetural e firmware próprio.
- [x] Executar os testes abaixo e registrar a regressão da nova versão.
- [x] Revisar perfil padrão, cobertura, documentação e evidências.
- [x] Integrar a imagem oficial e validar o término real em x4.

```bash
# Executar depois das correções, um comando por vez. Não inclui síntese.
make tb TB=tb_crc
make tb TB=tb_decoder
make tb TB=tb_core_crc
make simple-system
make regression
```

O protocolo do programa completo e seu recebimento estão em
[firmware/official/receipt.md](../../firmware/official/receipt.md).
A síntese permanece reservada ao usuário. P02 (sistema/sincronização) e a
interface final continuam questões separadas da definição de CRC.
