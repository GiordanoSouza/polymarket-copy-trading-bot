# 🤖 Polymarket Copytrading Bot

An automated copytrading bot for Polymarket that monitors and replicates trades from experienced traders in real-time using Supabase and Python.

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Risk Management](#risk-management)
- [Contributing](#contributing)
- [License](#license)
- [Important Warnings](#important-warnings)

## 🎯 About the Project

This bot allows you to automatically copy trades from successful traders on Polymarket. It monitors activities in real-time, applies customizable risk filters, and executes orders automatically with integrated capital management.

**Key Features:**
- ⚡ Real-time monitoring via Supabase Realtime
- 🎯 Advanced filtering system (odds, liquidity, slippage)
- 💰 Capital management with Kelly Criterion
- 🛡️ Protections: stop-loss, take-profit, time-stops
- 📊 Complete tracking of positions and history
- ⚙️ Highly configurable via YAML

## ✨ Features

### Real-Time Monitoring
- **Trades**: Detects new trades from target trader instantly
- **Positions**: Monitors opening of new positions
- **Updates**: Tracks changes in existing positions (P&L, size)

### Capital Management
- Sizing based on percentage of copied trader


## 🏗️ Architecture

```
┌─────────────────┐
│   Polymarket    │
│   API/Events    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐      ┌──────────────────┐
│   Supabase DB   │◄─────┤  Polling Scripts │
│  (PostgreSQL)   │      └──────────────────┘
└────────┬────────┘
         │ Realtime Subscription
         ↓
┌─────────────────┐
│   Main Bot      │
│  - Listeners    │
│  - Handlers     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Constraints    │
│  - Sizing       │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Order Maker    │
│ (py-clob-client)│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Polymarket     │
│  CLOB API       │
└─────────────────┘
```

### Data Flow

1. **Collection**: Scripts poll Polymarket API for trader activities
2. **Storage**: Data is inserted into Supabase (history and positions)
3. **Detection**: Bot detects changes via Supabase Realtime
4. **Processing**: Handlers apply filters and validations
5. **Execution**: Orders are sent to Polymarket CLOB API
6. **Tracking**: Positions are monitored continuously

## 📋 Prerequisites

- **Python 3.9+**
- **Polymarket account** with configured wallet
- **Supabase account** (free tier works)
- **USDC** in your Polymarket wallet for trading
- **Private Key** from your wallet (to sign orders)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/cute_poly.git
cd cute_poly
```

### 2. Create a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Supabase

Follow instructions in [`supabase/README.md`](supabase/README.md) to:
- Create necessary tables
- Obtain access credentials

## ⚙️ Configuration
### 1. Configure Environment Variables

Copy the example file and fill with your credentials:

```bash
cp env.example .env
```
Edit `.env` with your information:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Polymarket
PK=your-private-key-here
POLY_FUNDER=your-polymarket-proxy-address
PROXY_WALLET_SELF=your-wallet-address

# Trader to copy
TRADER_WALLET=trader-wallet-to-copy
```

📝 **See [`SETUP.md`](SETUP.md) for detailed instructions on obtaining each credential.**

### 2. Adjust the Strategy

Edit `config.yaml` to configure:

```yaml
bankroll: 1000  # Your capital in USDT
sizing:
  stake_whale_pct: 0.005  # Copy 0.5% of trader's size

```

## 🎮 Usage

### Run the Main Bot

```bash
cd scripts
python main.py
```

The bot will:
1. Load and validate configurations
2. Connect to Supabase
3. Start activity polling (background)
4. Start real-time listeners
5. Process and execute trades automatically

### Test Configuration

```bash
python scripts/config.py
```

This will validate your credentials and display a configuration summary.

## 📁 Project Structure

```
cute_poly/
├── scripts/
│   ├── main.py                      # Main bot with listeners
│   ├── config.py                    # Centralized config management
│   ├── make_orders.py               # Order execution on Polymarket
│   ├── get_player_history_new.py   # Fetch trade history
│   ├── get_player_positions.py     # Fetch current positions
│   ├── listen_to_order.py          # Order listener
│   └── constraints/
│       ├── eligibility.py           # Eligibility validations
│       ├── sizing.py                # Position size calculations
│       ├── risk.py                  # Risk controls
│       ├── exits.py                 # Exit logic
│       └── validators.py            # General validators
├── supabase/
│   ├── create_table.sql            # Database schema
│   ├── insert_activities.py        # Activity insertion
│   ├── polling_activities.py       # Continuous polling
│   └── README.md                   # Supabase docs
├── config.yaml                     # Strategy configuration
├── env.example                     # Environment variables template
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── SETUP.md                        # Detailed setup guide
├── CONTRIBUTING.md                 # Contribution guidelines
└── LICENSE                         # Project license
```

## 🤝 Contributing

Contributions are welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md) for:
- How to report bugs
- How to suggest features
- Code standards
- Pull Request process

### Areas Needing Help

- [ ] Web interface for monitoring
- [ ] Backtesting framework
- [ ] More sizing strategies
- [ ] Analytics dashboard
- [ ] Automated tests
- [ ] Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

### Support

- 📧 Issues: [GitHub Issues](https://github.com/yourusername/cute_poly/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/cute_poly/discussions)
- 📚 Docs: [Wiki](https://github.com/yourusername/cute_poly/wiki)

---

**Built with ❤️ for the Polymarket community**

*If this project helped you, consider giving it a ⭐ on GitHub!*
