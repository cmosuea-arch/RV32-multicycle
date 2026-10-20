# Recebimento do firmware oficial — preencher quando disponível

Ainda não há programa oficial recebido. Este arquivo organiza a conferência;
não define um novo formato, endereço de assinatura ou comportamento de término.

| Campo | Valor |
|---|---|
| Data, origem/link e versão | PENDENTE |
| Nome dos arquivos e SHA-256 | PENDENTE |
| Formato recebido: assembly, ELF, imagem ou outro | PENDENTE |
| Ferramenta/comando de montagem, se necessário | PENDENTE |
| Endereço de entrada e base da IMEM | PENDENTE |
| Tamanho, ordem das palavras/bytes e necessidade de padding | PENDENTE |
| Dados iniciais e capacidade da DMEM | PENDENTE |
| Inicialização da pilha e registradores pelo programa/TB | PENDENTE |
| Contrato CRC utilizado | PENDENTE |
| Instruções de sistema utilizadas | PENDENTE |
| Como detectar sucesso e primeira falha | PENDENTE |
| Timeout e etapas esperadas | PENDENTE |
| Commit RTL e logs/waveform da execução | PENDENTE |

## Ordem de integração

1. Preservar os arquivos originais e registrar seus hashes (`sha256sum arquivo`).
2. Conferir o contrato recebido antes de adaptar montagem, imagem ou TB.
3. Se houver fonte, montar/ligar conforme as instruções da organização; se já
   houver imagem, evitar recompilar ou reinterpretar a ordem dos bytes por suposição.
4. Carregar a imagem na IMEM parametrizada, preservando as bases arquiteturais
   ou registrando explicitamente uma exigência oficial diferente.
5. Criar/adaptar o teste com o protocolo oficial, timeout e diagnóstico da primeira
   falha. Não reutilizar a assinatura CMOS sem confirmação de que ela se aplica.
6. Executar firmware e regressão, arquivar log/waveform/hashes e atualizar o relatório.

Fluxo próprio de referência: [README.md](README.md). A resposta sobre CRC deve
ser registrada no [formulário do contrato](../../docs/architecture/crc_official_confirmation.md).
