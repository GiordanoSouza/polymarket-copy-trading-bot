# 📚 Documentação do Banco de Dados - Polymarket Activities

## 🎯 Visão Geral

Este documento explica a estrutura e configurações especiais da tabela `polymarket_activities`, incluindo a **Generated Column** que resolve o problema de duplicatas.

---

## 📋 Estrutura da Tabela

### Tabela: `polymarket_activities`

| Coluna | Tipo | Descrição | Especial |
|--------|------|-----------|----------|
| `id` | BIGSERIAL | Chave primária auto-incrementada | 🔑 Primary Key |
| `unique_activity_key` | VARCHAR(500) | **Chave única composta gerada automaticamente** | ⚡ **Generated Column** |
| `transaction_hash` | VARCHAR(255) | Hash da transação blockchain | |
| `condition_id` | TEXT | ID da condição do mercado | |
| `price` | NUMERIC | Preço unitário do trade | |
| ... | ... | Outras colunas normais | |

---

## 🔍 Onde Encontrar as Configurações no Supabase

### 1. **Supabase Dashboard - Table Editor**

**Caminho:** Dashboard → Table Editor → `polymarket_activities`

#### Como identificar a Generated Column:
1. Abra a tabela no Table Editor
2. Procure pela coluna `unique_activity_key`
3. Ela deve aparecer com um ícone especial ou indicador de "computed"
4. Clique na coluna para ver detalhes

### 2. **Supabase Dashboard - SQL Editor**

**Caminho:** Dashboard → SQL Editor

Execute esta query para ver todas as Generated Columns:

```sql
SELECT 
    table_name,
    column_name,
    data_type,
    generation_expression,
    is_generated
FROM information_schema.columns 
WHERE table_name = 'polymarket_activities' 
  AND is_generated = 'ALWAYS'
ORDER BY column_name;
```

**Resultado esperado:**
```
table_name: polymarket_activities
column_name: unique_activity_key
data_type: character varying
generation_expression: (((((transaction_hash)::text || '_'::text) || COALESCE(condition_id, 'null'::text)) || '_'::text) || COALESCE((price)::text, 'null'::text))
is_generated: ALWAYS
```

### 3. **Supabase Dashboard - Database**

**Caminho:** Dashboard → Database → Tables → `polymarket_activities`

1. Clique na tabela
2. Vá para a aba "Columns" ou "Schema"
3. A coluna `unique_activity_key` deve aparecer com um indicador especial

### 4. **Via SQL - Informações Completas**

```sql
-- Ver estrutura completa da tabela
\d polymarket_activities

-- Ou usando information_schema:
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default,
    generation_expression,
    is_generated,
    is_updatable
FROM information_schema.columns 
WHERE table_name = 'polymarket_activities' 
ORDER BY ordinal_position;
```

---

## 🗂️ Índices e Constraints

### Ver todos os índices:

```sql
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'polymarket_activities'
ORDER BY indexname;
```

**Índices importantes:**

| Nome | Tipo | Propósito |
|------|------|-----------|
| `idx_unique_activity_key` | **UNIQUE INDEX** | 🔑 **Previne duplicatas** |
| `idx_proxy_wallet` | INDEX | Buscar por usuário |
| `idx_timestamp` | INDEX | Ordenar por data |
| `idx_type` | INDEX | Filtrar por tipo |
| `idx_activity_datetime` | INDEX | Consultas temporais |

---

## 📖 Como Documentar para Novos Desenvolvedores

### 1. **Comentários no Banco de Dados**

```sql
-- Adicionar comentários explicativos
COMMENT ON TABLE polymarket_activities IS 
'Atividades do Polymarket com chave única composta para evitar duplicatas';

COMMENT ON COLUMN polymarket_activities.unique_activity_key IS 
'Chave única composta: transaction_hash + condition_id + price. Gerada automaticamente para evitar duplicatas de fills múltiplos.';

COMMENT ON INDEX idx_unique_activity_key IS 
'Índice único que previne inserção de atividades duplicadas. Essencial para polling sem duplicatas.';
```

### 2. **Arquivo README no Projeto**

Criar/atualizar `supabase/README.md`:

```markdown
# 🏗️ Banco de Dados - Polymarket

## ⚠️ Configurações Importantes

### Generated Column: `unique_activity_key`

**O que é:** Coluna calculada automaticamente que combina `transaction_hash + condition_id + price`

**Por que existe:** Resolve problema de duplicatas quando uma transação tem múltiplos fills

**Como funciona:** PostgreSQL calcula automaticamente quando uma linha é inserida

**Query para verificar:**
```sql
SELECT generation_expression FROM information_schema.columns 
WHERE table_name = 'polymarket_activities' AND column_name = 'unique_activity_key';
```

### Índice Único: `idx_unique_activity_key`

**Propósito:** Previne inserção de duplicatas
**Tipo:** UNIQUE INDEX
**Coluna:** `unique_activity_key`

## 🔧 Migrations

Ver arquivo: `create_table.sql` + migrations aplicadas via MCP
```

### 3. **Documentação no Código Python**

```python
# supabase/insert_activities.py
def insert_activities_batch(activities: list):
    """
    Insere atividades no Supabase usando upsert baseado na unique_activity_key
    
    IMPORTANTE: A coluna 'unique_activity_key' é uma Generated Column no PostgreSQL.
    Ela é calculada automaticamente baseada em: transaction_hash + condition_id + price
    
    Esta coluna resolve o problema de duplicatas quando uma transação tem múltiplos fills.
    
    Ver: supabase/DATABASE_DOCUMENTATION.md para mais detalhes
    """
```

---

## 🚨 Troubleshooting para Novos Desenvolvedores

### Problema: "unique constraint violated"

**Sintoma:** Erro ao inserir dados
**Causa:** Tentativa de inserir atividade duplicada
**Solução:** A Generated Column já previne isso automaticamente

### Problema: "column unique_activity_key does not exist"

**Sintoma:** Erro ao fazer query
**Causa:** Migration não foi aplicada
**Solução:** Verificar se a migration foi executada:

```sql
-- Verificar se a coluna existe
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'polymarket_activities' AND column_name = 'unique_activity_key';

-- Se não existir, aplicar migration:
-- (Ver arquivo de migration no MCP ou create_table.sql)
```

### Problema: Polling inserindo duplicatas

**Sintoma:** Mesmas atividades aparecem várias vezes
**Causa:** Script não está usando a verificação de unique_activity_key
**Solução:** Usar o script `polling_activities.py` que já tem a verificação

---

## 📊 Queries Úteis para Desenvolvedores

### Verificar Generated Column:

```sql
SELECT 
    column_name,
    generation_expression,
    is_generated
FROM information_schema.columns 
WHERE table_name = 'polymarket_activities' 
  AND is_generated = 'ALWAYS';
```

### Ver estatísticas da tabela:

```sql
SELECT 
    COUNT(*) as total_registros,
    COUNT(DISTINCT unique_activity_key) as chaves_unicas,
    COUNT(DISTINCT transaction_hash) as transacoes_unicas
FROM polymarket_activities;
```

### Ver duplicatas (deve retornar 0):

```sql
SELECT 
    unique_activity_key,
    COUNT(*) as quantidade
FROM polymarket_activities
GROUP BY unique_activity_key
HAVING COUNT(*) > 1;
```

### Ver exemplos de chaves geradas:

```sql
SELECT 
    transaction_hash,
    condition_id,
    price,
    unique_activity_key
FROM polymarket_activities
ORDER BY id DESC
LIMIT 5;
```

---

## 🎯 Para Desenvolvedores Novos

### Checklist de Entendimento:

- [ ] Entendeu o que é uma Generated Column
- [ ] Saber onde encontrar a configuração no Supabase Dashboard
- [ ] Conhece o problema que a coluna resolve (duplicatas)
- [ ] Entende como o polling funciona sem duplicatas
- [ ] Sabe como verificar se está funcionando
- [ ] Conhece os índices e constraints da tabela

### Próximos Passos:

1. **Explorar o Supabase Dashboard** - Table Editor, SQL Editor
2. **Executar queries de verificação** - Ver exemplos acima
3. **Testar o polling** - `python supabase/polling_activities.py`
4. **Ler a documentação completa** - `POLLING_SOLUTION.md`

---

## 📞 Suporte

Se um desenvolvedor novo tiver dúvidas:

1. **Verificar este documento** primeiro
2. **Consultar o Supabase Dashboard** - SQL Editor
3. **Executar queries de diagnóstico** - Ver seção "Queries Úteis"
4. **Verificar logs do polling** - Se aplicável

**Arquivos de referência:**
- `supabase/DATABASE_DOCUMENTATION.md` (este arquivo)
- `supabase/POLLING_SOLUTION.md` (solução completa)
- `supabase/polling_activities.py` (script de polling)
- `supabase/create_table.sql` (estrutura inicial)

