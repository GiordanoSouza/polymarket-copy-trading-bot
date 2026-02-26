CREATE TABLE historic_trades (
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


CREATE TABLE polymarket_positions (
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

ALTER TABLE historic_trades
ADD COLUMN unique_activity_key VARCHAR(500)
GENERATED ALWAYS AS (
    transaction_hash || '_' ||
    COALESCE(condition_id, 'null') || '_' ||
    COALESCE(price::text, 'null')
) STORED;

CREATE UNIQUE INDEX idx_unique_activity_key ON historic_trades (unique_activity_key);