# 🗄️ Supabase Database Setup
This directory contains all files necessary to configure the Supabase database for the copytrading bot.

### 1. Create Supabase Account
1. Go to [supabase.com](https://supabase.com/)
2. Click "Start your project"
3. Log in with GitHub or email
4. Create a new project (free plan works)

### 2. Obtain Credentials
1. In the project dashboard, go to **Settings** → **API**
2. Copy:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: Key starting with `eyJ...`
⚠️ **Use the `anon` key, NOT `service_role`!**

### 3. Execute SQL Script

1. On Supabase, go to **SQL Editor**
2. Click **+ New Query**
3. Copy all content from `create_table.sql`
4. Paste in the editor and click **Run** (or Ctrl+Enter)
5. Wait for "Success. No rows returned" message

### 4. Verify Creation

1. Go to **Table Editor**
2. You should see:
   - `historic_trades`
   - `polymarket_positions`

### 5. ⚠️ CRITICAL: Enable Realtime

**This step is required for the bot to work!** The bot uses Supabase Realtime to detect new trades instantly.

1. In your Supabase Dashboard, go to **Database** → **Replication**
2. Scroll down to find the **Realtime** section
3. Look for these tables in the list:
   - `historic_trades`
   - `polymarket_positions`
4. Click the **toggle switch** next to each table to enable Realtime (it should turn green)
5. Wait a few seconds for the changes to apply

**Visual Guide:**
```
┌─────────────────────────────────────┐
│  Replication                         │
├─────────────────────────────────────┤
│  Source: postgres.public            │
│                                      │
│  Tables:                             │
│  ☑ historic_trades        [●]       │  ← Enable this
│  ☑ polymarket_positions   [●]       │  ← Enable this
└─────────────────────────────────────┘
```

✅ Done! Your database is configured and ready to use.

### 6. Configure .env File

In the **project root** (not in the supabase folder), add to your `.env`:

```env
SUPABASE_URL=https://your-project-here.supabase.co
SUPABASE_KEY=your-anon-public-key-here
```

## 🔍 Troubleshooting

**Bot is not detecting trades?**
- ✅ Make sure Realtime is **enabled** for both tables (green toggle in Database → Replication)
- ✅ Verify your SUPABASE_URL and SUPABASE_KEY are correct in `.env`
- ✅ Check that the trader's wallet address is valid

**Realtime toggle not appearing?**
- Make sure you're on the free plan or higher (all plans support Realtime)
- Try refreshing the page or checking Database → Replication again

## 💡 Important: Generated Column

The `historic_trades` table has a special **Generated Column** (`unique_activity_key`) that automatically prevents duplicates. 

