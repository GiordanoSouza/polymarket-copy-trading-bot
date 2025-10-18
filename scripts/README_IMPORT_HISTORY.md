# 📊 Importação de Histórico de Players - Polymarket

## 📝 Descrição

Script Python para importar o histórico completo de trades de players do Polymarket para o banco de dados Supabase.

## 🎯 Funcionalidades

- ✅ Busca automática com paginação (offset) para superar o limite de 500 registros da API
- ✅ Filtragem por período (padrão: últimos 365 dias / 1 ano)
- ✅ Prevenção de duplicatas (usando `transaction_hash` como chave única)
- ✅ Suporte para múltiplos players em uma única execução
- ✅ Tratamento de erros e relatório detalhado
- ✅ Rate limiting automático para não sobrecarregar a API

## 🚀 Como Usar

### Pré-requisitos

1. Variáveis de ambiente configuradas no arquivo `.env`:
```env
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
```

2. Tabela `polymarket_activities` criada no Supabase (já feito ✓)

3. Dependências instaladas:
```bash
pip install requests supabase python-dotenv
```

### Importar um único player

```python
from import_player_history import import_player_history

# Importar histórico de 1 ano
player_address = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
import_player_history(player_address, days_back=365)
```

### Importar múltiplos players

```python
from import_player_history import import_multiple_players

players = [
    "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
    "0x1234567890abcdef1234567890abcdef12345678",
    "0xabcdef1234567890abcdef1234567890abcdef12",
]

import_multiple_players(players, days_back=365)
```

### Executar diretamente

Edite o final do arquivo `import_player_history.py` e execute:

```bash
python scripts/import_player_history.py
```

## 📋 Campos Salvos no Banco

O script salva os seguintes campos na tabela `polymarket_activities`:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `proxy_wallet` | VARCHAR | Endereço da carteira proxy |
| `timestamp` | BIGINT | Timestamp Unix da atividade |
| `activity_datetime` | TIMESTAMP | Data/hora formatada |
| `condition_id` | VARCHAR | ID da condição do mercado |
| `type` | VARCHAR | Tipo de atividade (TRADE, YIELD, etc) |
| `size` | NUMERIC | Quantidade de tokens |
| `usdc_size` | NUMERIC | Valor em USDC |
| `transaction_hash` | VARCHAR | Hash da transação (ÚNICO) |
| `price` | NUMERIC | Preço unitário |
| `asset` | TEXT | Ativo negociado |
| `side` | VARCHAR | Lado da operação (BUY/SELL) |
| `outcome_index` | INTEGER | Índice do resultado |
| `title` | TEXT | Título do mercado |
| `slug` | VARCHAR | Slug do mercado |
| `icon` | TEXT | URL do ícone |
| `event_slug` | VARCHAR | Slug do evento |
| `outcome` | VARCHAR | Resultado escolhido |
| `trader_name` | VARCHAR | Nome do trader |
| `pseudonym` | VARCHAR | Pseudônimo do trader |
| `bio` | TEXT | Biografia do trader |
| `profile_image` | TEXT | Imagem de perfil |
| `profile_image_optimized` | TEXT | Imagem otimizada |

## 🔄 Como Funciona a Paginação

1. O script faz requisições de 500 registros por vez (limite máximo da API)
2. Usa o parâmetro `offset` para buscar os próximos registros
3. Continua até:
   - Não haver mais registros
   - Encontrar registros fora do período especificado
   - Receber menos registros que o limite (última página)

## 📊 Exemplo de Saída

```
====================================================================================================
🚀 INICIANDO IMPORTAÇÃO DE HISTÓRICO
====================================================================================================
📍 Player: 0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b
📅 Período: Últimos 365 dias
🗄️  Tabela: polymarket_activities
====================================================================================================

📥 Buscando atividades (offset: 0, limit: 500)...
   ✓ Recebidas: 500 atividades
   ✓ No período: 500 atividades
   💾 Inserindo no Supabase...
   ✓ Inseridos: 485 | Duplicados: 15 | Erros: 0

📥 Buscando atividades (offset: 500, limit: 500)...
   ✓ Recebidas: 250 atividades
   ✓ No período: 250 atividades
   💾 Inserindo no Supabase...
   ✓ Inseridos: 250 | Duplicados: 0 | Erros: 0

====================================================================================================
📊 RESUMO DA IMPORTAÇÃO
====================================================================================================
📥 Total de atividades buscadas: 750
✅ Total inseridas com sucesso: 735
🔄 Total de duplicadas (ignoradas): 15
❌ Total de erros: 0
====================================================================================================
```

## ⚙️ Parâmetros Configuráveis

- **`days_back`**: Número de dias para buscar no histórico (padrão: 365)
- **`MAX_LIMIT`**: Limite de registros por requisição (fixo em 500 - máximo da API)
- **`time.sleep(0.5)`**: Delay entre requisições para não sobrecarregar a API

## 🛡️ Tratamento de Erros

- **Duplicatas**: Ignoradas automaticamente (transaction_hash é UNIQUE)
- **Erros de rede**: Reportados mas não interrompem a execução
- **Erros de inserção**: Registrados no console com detalhes

## 🔍 Dicas

1. **Primeira importação**: Use `days_back=365` para pegar todo o histórico
2. **Atualizações diárias**: Use `days_back=7` para pegar apenas os últimos dias
3. **Múltiplos players**: Use a função `import_multiple_players()` para eficiência
4. **Monitoramento**: Acompanhe os logs para identificar possíveis problemas

## 📞 API Utilizada

- **Endpoint**: `https://data-api.polymarket.com/activity`
- **Limite máximo**: 500 registros por requisição
- **Paginação**: Via parâmetro `offset`
- **Ordenação**: Por timestamp (DESC)

