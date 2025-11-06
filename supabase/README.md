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

✅ Done! Your database is configured.

### 5. Configure .env File

In the **project root** (not in the supabase folder), add to your `.env`:

```env
SUPABASE_URL=https://your-project-here.supabase.co
SUPABASE_KEY=your-anon-public-key-here
```

## ⚠️ Important: Generated Column

The `historic_trades` table has a special **Generated Column** (`unique_activity_key`) that automatically prevents duplicates. 

