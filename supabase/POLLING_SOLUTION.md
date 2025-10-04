# 🎯 Solução para Polling de Atividades - Copy Trading

## 📋 Problema Identificado

Na tabela `polymarket_activities`, alguns `transaction_hash` apareciam duplicados (9 hashes duplicados em 550 registros), impossibilitando seu uso como chave única para fazer polling sem adicionar linhas repetidas.

### Por que os hashes se repetem?

1. **Múltiplos fills em uma única transação**: Quando uma ordem grande é executada, ela pode ser "filled" (preenchida) em diferentes níveis de preço:
   - Exemplo: SELL de 2.954 tokens executado em 4 preços diferentes (0.401, 0.402, 0.403, 0.404)

2. **Múltiplos mercados em uma transação**: Um REDEEM pode resgatar posições de vários mercados simultaneamente:
   - Exemplo: 1 REDEEM que resgata posições em 3 mercados diferentes

## ✅ Solução Implementada

### 1. Chave Única Composta

Criada uma coluna `unique_activity_key` que combina:
```
transaction_hash + condition_id + price
```

Esta combinação garante que:
- Cada fill individual é único (mesmo hash, preços diferentes)
- Cada mercado é único (REDEEMs de múltiplos mercados)
- Não há duplicatas reais

### 2. Migration Aplicada

```sql
ALTER TABLE polymarket_activities 
ADD COLUMN unique_activity_key VARCHAR(500) 
GENERATED ALWAYS AS (
    transaction_hash || '_' || 
    COALESCE(condition_id, 'null') || '_' || 
    COALESCE(price::text, 'null')
) STORED;

CREATE UNIQUE INDEX idx_unique_activity_key 
ON polymarket_activities(unique_activity_key);
```

**Vantagens:**
- ✅ Coluna computed (calculada automaticamente)
- ✅ Índice único garante sem duplicatas
- ✅ Stored (armazenada fisicamente para melhor performance)

### 3. Script de Polling Atualizado

Criado `polling_activities.py` que:
- 🔄 Faz polling contínuo da API do Polymarket
- 🔍 Verifica se cada atividade já existe usando `unique_activity_key`
- ➕ Insere apenas novas atividades
- ⏭️ Ignora atividades já existentes
- 📊 Mostra estatísticas de cada poll

## 🚀 Como Usar

### Executar o Polling Manual (uma vez)

```bash
python supabase/insert_activities.py
```

**Saída esperada:**
```
✅ 45 atividades inseridas | 5 já existiam (puladas)
```

### Executar Polling Contínuo

```bash
python supabase/polling_activities.py
```

**O que faz:**
- Consulta a API a cada 60 segundos (configurável)
- Insere apenas atividades novas
- Roda indefinidamente até você pressionar Ctrl+C
- Mostra estatísticas em tempo real

**Saída esperada:**
```
🎯 POLYMARKET ACTIVITY POLLING - COPY TRADING
================================================================================
Usuário: 0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b
Intervalo: 60s
Limite por consulta: 100
================================================================================
📅 Última atividade no banco: 03/10/2025 23:09:37

[2025-10-04 15:30:00] 📊 Poll #1
   ✅ 3 novas atividades inseridas
   ⏭️  97 atividades já existiam (ignoradas)
   📈 Última: TRADE - Will Trump meet with Xi Jinping in 2025?... (03/10/2025 23:09:37)
   ⏳ Aguardando 60s até próximo poll...

[2025-10-04 15:31:00] 📊 Poll #2
   ⏭️  100 atividades já existiam (ignoradas)
   ⏳ Aguardando 60s até próximo poll...
```

### Configurar Intervalo de Polling

Edite em `polling_activities.py`:

```python
def main():
    USER_ADDRESS = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
    INTERVAL_SECONDS = 60  # Mude para 30, 120, 300, etc.
    LIMIT = 100  # Quantas atividades buscar por vez
```

**Recomendações:**
- ⚡ Para copy trading em tempo real: 30-60 segundos
- 🔋 Para histórico/análise: 300-600 segundos (5-10 minutos)
- ⚠️ Não use menos de 10 segundos para não sobrecarregar a API

## 📊 Verificar Dados

### Ver estatísticas da tabela

```sql
SELECT 
    COUNT(*) as total_registros,
    COUNT(DISTINCT transaction_hash) as transacoes_unicas,
    COUNT(DISTINCT unique_activity_key) as activities_unicas,
    MIN(activity_datetime) as primeira_atividade,
    MAX(activity_datetime) as ultima_atividade
FROM polymarket_activities;
```

### Ver hashes duplicados (antes tinham, agora são únicos)

```sql
SELECT 
    transaction_hash,
    COUNT(*) as fills,
    ARRAY_AGG(price) as precos_executados
FROM polymarket_activities
GROUP BY transaction_hash
HAVING COUNT(*) > 1
ORDER BY fills DESC;
```

### Ver últimas atividades inseridas

```sql
SELECT 
    type,
    side,
    title,
    size,
    price,
    activity_datetime,
    unique_activity_key
FROM polymarket_activities 
ORDER BY created_at DESC 
LIMIT 10;
```

## 🎯 Para Copy Trading

Agora que você tem os dados históricos corretos e polling contínuo, pode:

1. **Monitorar trades em tempo real**
```sql
SELECT * FROM polymarket_activities 
WHERE type = 'TRADE'
  AND activity_datetime > NOW() - INTERVAL '5 minutes'
ORDER BY activity_datetime DESC;
```

2. **Calcular performance**
```sql
SELECT 
    DATE(activity_datetime) as data,
    COUNT(*) as num_trades,
    SUM(CASE WHEN side = 'BUY' THEN usdc_size ELSE 0 END) as volume_compra,
    SUM(CASE WHEN side = 'SELL' THEN usdc_size ELSE 0 END) as volume_venda
FROM polymarket_activities
WHERE type = 'TRADE'
GROUP BY DATE(activity_datetime)
ORDER BY data DESC;
```

3. **Identificar mercados favoritos**
```sql
SELECT 
    title,
    COUNT(*) as num_trades,
    SUM(usdc_size) as volume_total,
    AVG(price) as preco_medio
FROM polymarket_activities
WHERE type = 'TRADE'
GROUP BY title
ORDER BY volume_total DESC
LIMIT 10;
```

4. **Criar trigger para notificações**
```sql
-- Você pode criar uma função que dispara quando novas atividades são inseridas
-- e envia para um webhook ou Edge Function do Supabase para copy trading automático
```

## 🔧 Troubleshooting

### Erro: "unique constraint violated"
✅ Resolvido! A solução com `unique_activity_key` previne isso automaticamente.

### Polling não encontra novas atividades
- Verifique se o usuário teve atividade recente no Polymarket
- Aumente o LIMIT se o usuário for muito ativo

### Muitas requisições à API
- Aumente o `INTERVAL_SECONDS`
- A API do Polymarket tem rate limiting

## 📚 Próximos Passos

1. **Automatizar com Cron/Systemd**: Manter o polling rodando 24/7
2. **Notificações**: Webhook quando nova atividade é detectada
3. **Copy Trading Automático**: Edge Function que executa trades automaticamente
4. **Dashboard**: Visualizar métricas em tempo real
5. **Múltiplos Traders**: Monitorar vários endereços simultaneamente

## 🎉 Conclusão

Com esta solução:
- ✅ Não há mais duplicatas na tabela
- ✅ Polling funciona perfeitamente
- ✅ Dados históricos completos e corretos
- ✅ Base sólida para copy trading

Todos os 550 registros agora têm uma `unique_activity_key` única, e novos registros são inseridos apenas se não existirem!


