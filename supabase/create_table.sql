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



CREATE TABLE IF NOT EXISTS polymarket_positions (
    proxy_wallet        CHAR(42)        NOT NULL,
    asset               NUMERIC(78, 0)  NOT NULL,
    condition_id        CHAR(66)        NOT NULL,
    size                NUMERIC(20, 6)  NOT NULL,
    avg_price           NUMERIC(10, 6)  NOT NULL,
    initial_value       NUMERIC(24, 6)  NOT NULL,
    current_value       NUMERIC(24, 6)  NOT NULL,
    cash_pnl            NUMERIC(24, 6)  NOT NULL,
    percent_pnl         NUMERIC(10, 6)  NOT NULL,
    total_bought        NUMERIC(24, 6)  NOT NULL,
    realized_pnl        NUMERIC(24, 6)  NOT NULL,
    percent_realized_pnl NUMERIC(10, 6) NOT NULL,
    cur_price           NUMERIC(10, 6)  NOT NULL,
    redeemable          BOOLEAN         NOT NULL,
    mergeable           BOOLEAN         NOT NULL,
    title               VARCHAR(255)    NOT NULL,
    slug                VARCHAR(255)    NOT NULL,
    icon                TEXT            NOT NULL,
    event_id            BIGINT          NULL,
    event_slug          VARCHAR(255)    NOT NULL,
    outcome             VARCHAR(32)     NOT NULL,
    outcome_index       SMALLINT        NOT NULL,
    opposite_outcome    VARCHAR(32)     NOT NULL,
    opposite_asset      NUMERIC(78, 0)  NOT NULL,
    end_date            DATE            NULL,
    negative_risk       BOOLEAN         NOT NULL,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (proxy_wallet, asset)
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


