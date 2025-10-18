-- Tabela para armazenar atividades do Polymarket
CREATE TABLE IF NOT EXISTS polymarket_activities (
    id BIGSERIAL PRIMARY KEY,
    proxy_wallet VARCHAR(255) NOT NULL,
    timestamp BIGINT NOT NULL,
    activity_datetime TIMESTAMP WITH TIME ZONE,
    condition_id VARCHAR(255),
    type VARCHAR(50) NOT NULL,
    size NUMERIC(20, 6),
    usdc_size NUMERIC(20, 6),
    transaction_hash VARCHAR(255),
    price NUMERIC(20, 10),
    asset TEXT,
    side VARCHAR(10),
    outcome_index INTEGER,
    title TEXT,
    slug VARCHAR(255),
    icon TEXT,
    event_slug VARCHAR(255),
    outcome VARCHAR(50),
    trader_name VARCHAR(255),
    pseudonym VARCHAR(255),
    bio TEXT,
    profile_image TEXT,
    profile_image_optimized TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para melhorar performance de consultas
CREATE INDEX IF NOT EXISTS idx_proxy_wallet ON polymarket_activities(proxy_wallet);
CREATE INDEX IF NOT EXISTS idx_timestamp ON polymarket_activities(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_type ON polymarket_activities(type);
CREATE INDEX IF NOT EXISTS idx_event_slug ON polymarket_activities(event_slug);
CREATE INDEX IF NOT EXISTS idx_activity_datetime ON polymarket_activities(activity_datetime DESC);

-- Comentários nas colunas
COMMENT ON TABLE polymarket_activities IS 'Armazena todas as atividades (trades, yields, etc) dos usuários do Polymarket';
COMMENT ON COLUMN polymarket_activities.proxy_wallet IS 'Endereço da carteira proxy do usuário';
COMMENT ON COLUMN polymarket_activities.timestamp IS 'Unix timestamp da atividade';
COMMENT ON COLUMN polymarket_activities.activity_datetime IS 'Data/hora convertida da atividade';
COMMENT ON COLUMN polymarket_activities.transaction_hash IS 'Hash único da transação na blockchain';
COMMENT ON COLUMN polymarket_activities.type IS 'Tipo de atividade: TRADE, YIELD, etc';
COMMENT ON COLUMN polymarket_activities.side IS 'Lado da operação: BUY ou SELL';


