
```bash
pip install -r requirements.txt
```

Wait for all packages to install (~2-5 minutes).

---

## 3. Polymarket Configuration

### 3.1 Create/Connect Account

1. Go to [polymarket.com](https://polymarket.com/)
2. Click "Sign Up" or "Connect Wallet"
3. Choose your login method:
   - **Email/Magic Link** (easier)
   - **MetaMask** or another Web3 wallet

### 3.2 Obtain Your Private Key

The private key is necessary for the bot to sign transactions.

#### If using Email/Magic Link:

1. Log in to Polymarket
2. Go to [reveal.magic.link/polymarket](https://reveal.magic.link/polymarket)
3. Log in with the same email
4. Click "Reveal Private Key"
5. **COPY and SAVE SECURELY** (never share!)

#### If using MetaMask/Web3 Wallet:

1. Open MetaMask
2. Click on the 3 dots → Account Details
3. Click "Export Private Key"
4. Enter your password
5. **COPY and SAVE SECURELY**

⚠️ **IMPORTANT**: The private key gives full access to your funds. Never share!

### 3.3 Obtain Your Polymarket Proxy Address

1. Go to [polymarket.com](https://polymarket.com/)
2. Log in
3. Click on your profile (top right corner)
4. The address shown **below your profile picture** is your Proxy Address
5. Copy this address (format: `0x...`)

This is different from your main wallet address!

### 3.4 Find a Trader to Copy

1. Go to [polymarket.com/leaderboard](https://polymarket.com/leaderboard)
2. Choose a trader with:
   - ✅ Consistent volume
   - ✅ Positive ROI
   - ✅ At least 30 days of history
   - ✅ Trading style you agree with
3. Click on the trader
4. Copy their wallet address (in URL or profile)

### 3.5 Add USDC to Wallet

1. On Polymarket, click "Add Funds"
2. Choose the method:
   - Credit card (faster, higher fees)
   - Transfer from another wallet
   - Bridge from another chain
3. Add at least $50-$100 for testing

---

## 4. Supabase Configuration

### 4.1 Create Supabase Account

1. Go to [supabase.com](https://supabase.com/)
2. Click "Start your project"
3. Log in with GitHub or email
4. It's **free** for up to 500MB of data

### 4.2 Create a New Project

1. On the dashboard, click "New Project"
2. Fill in:
   - **Name**: `polymarket-bot` (or any name)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
   - **Pricing Plan**: Free (enough to start)
3. Click "Create new project"
4. Wait ~2 minutes for project provisioning

### 4.3 Obtain Supabase API Credentials

1. In the created project, go to **Settings** (⚙️ icon in sidebar)
2. Click **API** in the sidebar
3. In the **Project API keys** section, you'll see:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public**: `eyJhbGc...` (long key)
   - **service_role**: `eyJhbGc...` (DON'T use this!)

4. Copy both and save them securely

⚠️ Use the **`anon`** key, NOT the `service_role`!

### 4.4 Create Database Tables

1. On Supabase, go to **SQL Editor** (database icon)
2. Click **+ New query**
3. Open the `supabase/create_table.sql` file in your project
4. **Copy ALL the content** (Ctrl+A, Ctrl+C)
5. **Paste** in Supabase SQL Editor (Ctrl+V)
6. Click **Run** (or press Ctrl+Enter)

You will see:
```
Success. No rows returned
```

This creates two tables:
- `historic_trades`: Trade history
- `polymarket_positions`: Current positions

### 4.5 Verify Tables Created

1. Click **Table Editor** in the sidebar
2. You should see the tables:
   - ✅ `historic_trades`
   - ✅ `polymarket_positions`
3. Click on each to see the structure

### 4.6 Configure Row Level Security (Optional)

By default, RLS is disabled on the tables. For production, consider enabling:

```sql
-- Enable RLS
ALTER TABLE historic_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE polymarket_positions ENABLE ROW LEVEL SECURITY;

-- Allow read/write for anon key
CREATE POLICY "Allow all operations" ON historic_trades
  FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations" ON polymarket_positions
  FOR ALL USING (true) WITH CHECK (true);
```

### 4.7 Test Connection

In the bot directory, run:

```bash
python scripts/config.py
```

Should display:
```
✅ Configuration loaded successfully!
📊 Supabase URL: https://xxxxx.supabase.co
```

If there's an error, review the previous steps.

---

## 5. Environment Variables Configuration

### 5.1 Copy Template

```bash
cp env.example .env
```

**Windows (if cp doesn't work):**
- Manually copy the `env.example` file
- Paste in the same folder
- Rename to `.env`

### 5.2 Edit the .env File

Open `.env` with a text editor and fill in:

```env
# ==========================================
# SUPABASE CONFIGURATION
# ==========================================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# ==========================================
# POLYMARKET CONFIGURATION
# ==========================================
PK=your-private-key-here
POLY_FUNDER=your-proxy-address-here
CLOB_API_URL=https://clob.polymarket.com
POLY_CHAIN_ID=137

# ==========================================
# TRADER TO COPY
# ==========================================
PROXY_WALLET_SELF=your-wallet-address-here
TRADER_WALLET=trader-wallet-to-copy
```

### 5.3 Completion Checklist

- [ ] `SUPABASE_URL`: Supabase URL (Step 4.3)
- [ ] `SUPABASE_KEY`: Supabase Anon key (Step 4.3)
- [ ] `PK`: Your private key (Step 3.2)
- [ ] `POLY_FUNDER`: Your Polymarket proxy address (Step 3.3)
- [ ] `PROXY_WALLET_SELF`: Your wallet address
- [ ] `TRADER_WALLET`: Trader's wallet to copy (Step 3.4)

---

## 6. Strategy Configuration

### 6.1 Edit config.yaml

Open `config.yaml` and adjust the values:

```yaml
# Your available capital
bankroll: 100  # Start with small value for testing!

sizing:
  stake_min: 5       # Minimum per trade
  stake_max: 20      # Maximum per trade
  stake_whale_pct: 0.005  # Copy 0.5% of trader's size
  
exits:
  take_profit_pct: 0.20   # Close with +20% profit
  stop_loss_pct: -0.10    # Close with -10% loss
```

### 6.2 Initial Recommendations

To start, use **conservative** values:

```yaml
bankroll: 50-100

sizing:
  stake_min: 2
  stake_max: 10
  stake_whale_pct: 0.001  # 0.1% = ultra conservative
  max_exposure_per_market_pct: 0.10  # Maximum 10% in one market
  
exits:
  take_profit_pct: 0.15   # Exit with +15%
  stop_loss_pct: -0.08    # Exit with -8%
  time_stop_days: 3       # Exit after 3 days if no movement
```

### 6.3 Understanding Parameters

**`stake_whale_pct`**: If trader bets $10,000:
- `0.001` = You bet $10
- `0.005` = You bet $50
- `0.01` = You bet $100

Adjust based on their capital vs your capital.

---

## 7. First Test

### 7.1 Test Configuration

```bash
cd scripts
python config.py
```

Should display:
```
⚙️ CONFIGURATION LOADED
📊 Supabase URL: https://...
🔗 CLOB API: https://clob.polymarket.com
...
✅ Configuration loaded successfully!
```

If there are errors, review previous steps.

### 7.2 Test Supabase Connection

```bash
python get_player_history_new.py
```

Enter trader's wallet when prompted. Should:
1. Fetch trades from API
2. Insert into Supabase
3. Display "Success count: X"

### 7.3 Run Bot (Observation Mode)

Before running, **temporarily comment out** the order execution line:

In `scripts/main.py`, find and comment these lines:

```python
# response = make_order(price=price, size=sized_value, side=BUY, token_id=asset)
print(f"[TEST MODE] Order that would be placed: {price}, {sized_value}, {side}, {token_id}")
```

Then run:

```bash
python main.py
```

The bot will:
- ✅ Connect to Supabase
- ✅ Start listeners
- ✅ Detect trades
- ❌ **NOT** execute orders (commented out)

Observe for 30-60 minutes to verify it detects activities.

### 7.4 Enable Real Execution

When comfortable:

1. Uncomment the lines in `main.py`
2. **Start with SMALL bankroll** ($50-$100)
3. Run: `python main.py`
4. **MONITOR CONSTANTLY** for the first hours

---

## 8. Troubleshooting

### Error: "ModuleNotFoundError"

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

### Error: "Configuration Errors: SUPABASE_URL is not set"

**Cause**: `.env` file not found or empty

**Solution**:
1. Verify `.env` exists in project root
2. Verify variables are filled in
3. Restart terminal and activate venv again

### Error: "Invalid API key" from Supabase

**Cause**: Incorrect Supabase key

**Solution**:
1. Verify you used **`anon`** key, not `service_role`
2. Copy again from Supabase (Settings → API)
3. Check for extra spaces in `.env`

### Error: "Insufficient balance"

**Cause**: Not enough USDC in wallet

**Solution**:
1. Add more USDC to your Polymarket wallet
2. Reduce `stake_min` and `stake_max` in `config.yaml`

### Bot doesn't detect trades

**Possible causes**:

1. **Trader isn't making trades**
   - Wait longer
   - Choose a more active trader

2. **Incorrect wallet address**
   - Verify you copied the correct address
   - Try manual fetch: `python get_player_history_new.py`

3. **Supabase Realtime not connected**
   - Check logs in console
   - Restart the bot

### Orders are not being executed

**Possible causes**:

1. **Filters too restrictive**
   - Adjust `odds_min/max` in `config.yaml`
   - Reduce `min_book_depth_multiple`

2. **Stake too small**
   - Calculated trade is < `stake_min`
   - Increase `stake_whale_pct` or reduce `stake_min`

3. **No liquidity in market**
   - Bot is protecting you
   - This is expected and healthy

### How to see detailed logs?

The bot already prints logs to console. To save to file:

**Linux/Mac:**
```bash
python main.py 2>&1 | tee bot.log
```

**Windows:**
```bash
python main.py > bot.log 2>&1
```

---

## 🎉 Next Steps

After complete setup:

1. ✅ **Monitor daily** for 1 week
2. ✅ **Keep logs** of all trades
3. ✅ **Adjust parameters** based on performance
4. ✅ **Increase capital** gradually
5. ✅ **Contribute** improvements to the project!

### Additional Resources

- 📖 [README.md](README.md) - Project overview
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- 💬 [GitHub Issues](https://github.com/yourusername/cute_poly/issues) - Report bugs
- 📚 [Polymarket Documentation](https://docs.polymarket.com/)
- 📚 [Supabase Documentation](https://supabase.com/docs)

---

## ❓ Need Help?

- **Bugs**: Open an [Issue on GitHub](https://github.com/yourusername/cute_poly/issues)
- **Questions**: Use [GitHub Discussions](https://github.com/yourusername/cute_poly/discussions)
- **Suggestions**: Pull Requests are welcome!

**Good luck and trade responsibly! 🚀**
