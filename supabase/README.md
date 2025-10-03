# Supabase - Polymarket Activities

## Configuração

### 1. Criar arquivo `.env`

Na raiz do projeto, crie um arquivo `.env` com suas credenciais do Supabase:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon-key
```

**Como obter as credenciais:**
1. Acesse seu projeto no [Supabase](https://app.supabase.com)
2. Vá em Settings > API
3. Copie a `URL` e a `anon/public` key

### 2. Criar a tabela no Supabase

Execute o SQL no Supabase SQL Editor:

1. No dashboard do Supabase, vá em **SQL Editor**
2. Clique em **New Query**
3. Cole o conteúdo do arquivo `create_table.sql`
4. Execute o script (botão Run ou Ctrl+Enter)

### 3. Instalar dependências

```bash
pip install supabase requests python-dotenv
```

### 4. Executar o script

```bash
python supabase/insert_activities.py
```

## Estrutura da Tabela

### `polymarket_activities`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | BIGSERIAL | ID único auto-incrementado |
| `proxy_wallet` | VARCHAR(255) | Endereço da carteira proxy |
| `timestamp` | BIGINT | Unix timestamp da atividade |
| `activity_datetime` | TIMESTAMP | Data/hora convertida |
| `condition_id` | VARCHAR(255) | ID da condição do mercado |
| `type` | VARCHAR(50) | Tipo: TRADE, YIELD, etc |
| `size` | NUMERIC | Quantidade de tokens |
| `usdc_size` | NUMERIC | Valor em USDC |
| `transaction_hash` | VARCHAR(255) | Hash da transação (único) |
| `price` | NUMERIC | Preço unitário |
| `asset` | TEXT | ID do ativo |
| `side` | VARCHAR(10) | BUY ou SELL |
| `outcome_index` | INTEGER | Índice do resultado |
| `title` | TEXT | Título do mercado |
| `slug` | VARCHAR(255) | Slug do mercado |
| `icon` | TEXT | URL do ícone |
| `event_slug` | VARCHAR(255) | Slug do evento |
| `outcome` | VARCHAR(50) | Resultado (Yes/No) |
| `trader_name` | VARCHAR(255) | Nome do trader |
| `pseudonym` | VARCHAR(255) | Pseudônimo do trader |
| `bio` | TEXT | Biografia do trader |
| `profile_image` | TEXT | URL da imagem de perfil |
| `profile_image_optimized` | TEXT | URL da imagem otimizada |
| `created_at` | TIMESTAMP | Data de criação do registro |
| `updated_at` | TIMESTAMP | Data de atualização |

## Índices

- `idx_proxy_wallet`: Para buscar atividades por usuário
- `idx_timestamp`: Para ordenar por data
- `idx_type`: Para filtrar por tipo de atividade
- `idx_event_slug`: Para buscar por evento específico
- `idx_activity_datetime`: Para consultas temporais

## Consultas Úteis

### Buscar todas as atividades de um usuário

```sql
SELECT * FROM polymarket_activities 
WHERE proxy_wallet = '0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b'
ORDER BY timestamp DESC;
```

### Buscar apenas trades

```sql
SELECT * FROM polymarket_activities 
WHERE type = 'TRADE'
ORDER BY timestamp DESC;
```

### Calcular volume total por usuário

```sql
SELECT 
    proxy_wallet,
    trader_name,
    COUNT(*) as total_trades,
    SUM(usdc_size) as volume_total
FROM polymarket_activities
WHERE type = 'TRADE'
GROUP BY proxy_wallet, trader_name
ORDER BY volume_total DESC;
```

### Buscar atividades recentes (últimas 24h)

```sql
SELECT * FROM polymarket_activities 
WHERE activity_datetime > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

## Próximos Passos

1. **Automação**: Criar um cron job para buscar atividades periodicamente
2. **Dashboard**: Criar visualizações no Supabase ou integrar com ferramentas como Metabase
3. **Alertas**: Configurar notificações para trades grandes
4. **Analytics**: Criar views agregadas para análises de desempenho


