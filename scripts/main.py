import asyncio
from datetime import datetime
import threading
import time
import traceback
from supabase import acreate_client, AsyncClient
from make_orders import make_order
from get_player_positions import fetch_player_positions, insert_player_positions_batch
from get_player_history_new import (
    fetch_activities as fetch_history_activities,
    insert_activities_batch as insert_history_batch,
)
from constraints.sizing import sizing_constraints
from py_clob_client.order_builder.constants import BUY, SELL
from config import get_config

# Load configuration
config = get_config()

# Config Supabase (from centralized config)
url: str = config.SUPABASE_URL
key: str = config.SUPABASE_KEY
trader_wallet = config.TRADER_WALLET
TABLE_NAME_TRADES = config.TABLE_NAME_TRADES
TABLE_NAME_POSITIONS = config.TABLE_NAME_POSITIONS

# Cliente Supabase compartilhado
_supabase_client: AsyncClient = None

async def get_supabase() -> AsyncClient:
    """
    Returns a singleton instance of the Supabase client
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = await acreate_client(url, key)
    return _supabase_client


def handle_new_trade(payload):
    """
    Handler for new inserted trades
    """
    try:
        record = payload.get('data', {}).get('record', {})
        transaction_hash = record.get('transaction_hash')
        usdc_size = record.get('usdc_size')
        side = record.get('side')
        token_id = record.get('asset')
        title = record.get('title')
        price = record.get('price')
        size = record.get('size')
        proxy_wallet = record.get('proxy_wallet')
        condition_id = record.get('condition_id')
        
        print("\n" + "=" * 100)
        print(f"🔍 New trade received! [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"📝 Title: {title}")
        print(f"🔑 Transaction Hash: {transaction_hash}")
        print(f"💰 USDC Size: {usdc_size}")
        print(f"📊 Side: {side}")
        print(f"🎯 Token ID: {token_id}")
        print(f"💵 Price: {price}")
        print("=" * 100)

        if side == SELL:
            print(f"⏭️  Side is SELL, checking the % of the position from the TRADER")
            data_trader = fetch_player_positions(user_address=proxy_wallet, condition_id=condition_id)
            data_myself = fetch_player_positions(user_address=trader_wallet, condition_id=condition_id)
            size_trader = data_trader[0].get('size')
            size_myself = data_myself[0].get('size')
            percentage_position = usdc_size / size_trader
            final_size = percentage_position*size_myself
            response = make_order(price=price, size=final_size, side=side, token_id=token_id)
            print(f"📤 Response: {response}")
            return response 
        else:
            print(f"⏭️  Side is BUY, checking if size is greater than 1")
            sized_usdc = sizing_constraints(usdc_size)
            sized_size = sizing_constraints(size)
            if sized_usdc >= 1:
                print(f"✅ Sized USDC ({sized_usdc}) >= 1, placing order with size {sized_size}...")
                response = make_order(price=price, size=sized_size, side=side, token_id=token_id)
                print(f"📤 Response: {response}")
                return response
            else:
                print(f"⏭️  Sized USDC ({sized_usdc}) < 1, skipping order")
                return None
    except Exception as e:
        print(f"❌ Error processing new trade: {e}")
        return None


def handle_new_position(payload):
    """
    Handler for new inserted positions
    """
    try:
        record = payload.get('data', {}).get('record', {})
        
        # Campos do Polymarket (camelCase)
        asset = record.get('asset')
        initial_value = record.get('initialValue') 
        size = record.get('size')
        avg_price = record.get('avgPrice', 0)
        title = record.get('title', 'N/A')
        outcome = record.get('outcome', 'N/A')
        proxy_wallet = record.get('proxyWallet', 'N/A')

        print("\n" + "=" * 100)
        print(f"📈 New position received! [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"📝 Title: {title}")
        print(f"🎲 Outcome: {outcome}")
        print(f"🎯 Asset: {asset}")
        print(f"💰 Initial Value: ${initial_value:.4f}")
        print(f"📊 Size: {size}")
        print(f"💵 Avg Price: ${avg_price:.4f}")
        print(f"👛 Wallet: {proxy_wallet[:10]}...")
        print("=" * 100)

        sized_value = sizing_constraints(initial_value)
        
        if sized_value > 1:
            print(f"✅ Sized value ({sized_value}) > 1, placing buy order...")
            response = make_order(price=avg_price, size=sizing_constraints(size), side=BUY, token_id=asset)
            print(f"📤 Response: {response}")
            return response 
        else:
            print(f"⏭️  Sized value ({sized_value}) <= 1, skipping position")
            return None
    except Exception as e:
        print(f"❌ Error processing new position: {e}")
        traceback.print_exc()
        return None


def handle_update_position(payload):
    """
    Handler for updates to existing positions
    """
    try:
        old_record = payload.get('data', {}).get('old_record', {})
        new_record = payload.get('data', {}).get('record', {})
        
        # Campos do Polymarket (camelCase)
        asset = new_record.get('asset')
        title = new_record.get('title', 'N/A')
        outcome = new_record.get('outcome', 'N/A')
        
        old_value = old_record.get('current_value', 0)  # ✅ Corrigido: camelCase
        new_value = new_record.get('current_value', 0)  # ✅ Corrigido: camelCase
        old_size = old_record.get('size', 0)
        new_size = new_record.get('size', 0)
        
        # PnL information
        cash_pnl = new_record.get('cash_pnl', 0)
        percent_pnl = new_record.get('percent_pnl', 0)
        cur_price = new_record.get('cur_price', 0)
        avg_price = new_record.get('avg_price', 0)
        
        print("\n" + "=" * 100)
        print(f"🔄 Position update received! [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"📝 Title: {title}")
        print(f"🎲 Outcome: {outcome}")
        print(f"🎯 Asset: {asset}")
        print(f"💰 Value: ${old_value:.4f} → ${new_value:.4f} (Δ: ${new_value - old_value:+.4f})")
        print(f"📊 Size: {old_size} → {new_size} (Δ: {new_size - old_size:+.2f})")
        print(f"💵 Price: Avg ${avg_price:.4f} | Current ${cur_price:.4f}")
        print(f"📈 PnL: ${cash_pnl:+.4f} ({percent_pnl:+.1f}%)")
        print("=" * 100)
        

        sized_value = sizing_constraints(new_value - old_value)
        if sized_value > 1:
            print(f"✅ Sized value ({sized_value}) > 1, placing buy order...")
            response = make_order(price=avg_price, size=sized_value, side=BUY, token_id=asset)
            print(f"📤 Response: {response}")
            return response
        elif sized_value <= -1:
            print(f"⏭️  Sized value ({sized_value}) <= -1, placing sell order...")
            response = make_order(price=avg_price, size=sized_value, side=SELL, token_id=asset)
            print(f"📤 Response: {response}")
            return response
        else:
            print(f"⏭️  Sized value ({sized_value}) did not meet the criteria")
            return None
    except Exception as e:
        print(f"❌ Error processing position update: {e}")
        traceback.print_exc()
        return None

async def listen_to_positions():
    """
    Starts listener for new positions (INSERTs)
    """
    print("🔍 Starting positions listener...")
    print(f"📊 Monitoring table: {TABLE_NAME_POSITIONS} (INSERT)")
    
    try:
        # Usar cliente compartilhado
        supabase = await get_supabase()

        response = (
            await supabase.channel("positions-inserts")
            .on_postgres_changes("INSERT", schema="public", table=TABLE_NAME_POSITIONS, callback=handle_new_position)
            .subscribe()
        )
        
        print("✅ Positions listener connected!\n")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        print("🛑 Positions listener cancelled")
        if 'response' in locals():
            await response.unsubscribe()
        raise
    except Exception as e:
        print(f"❌ Error in positions listener: {e}")
        raise

async def listen_to_updates():
    """
    Starts listener for position updates (UPDATEs)
    """
    print("🔍 Starting updates listener...")
    print(f"📊 Monitoring table: {TABLE_NAME_POSITIONS} (UPDATE)")
    
    try:
        # Usar cliente compartilhado
        supabase = await get_supabase()
        
        response = (
            await supabase.channel("positions-updates")
            .on_postgres_changes("UPDATE", schema="public", table=TABLE_NAME_POSITIONS, callback=handle_update_position)
            .subscribe()
        )

        print("✅ Updates listener connected!\n")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        print("🛑 Updates listener cancelled")
        if 'response' in locals():
            await response.unsubscribe()
        raise
    except Exception as e:
        print(f"❌ Error in updates listener: {e}")
        raise

async def listen_to_trades():
    """
    Starts listener for new trades (INSERTs)
    """
    print("🔍 Starting trades listener...")
    print(f"📊 Monitoring table: {TABLE_NAME_TRADES} (INSERT)")
    
    try:
        # Usar cliente compartilhado
        supabase = await get_supabase()

        response = (
            await supabase.channel("trades-inserts")
            .on_postgres_changes("INSERT", schema="public", table=TABLE_NAME_TRADES, callback=handle_new_trade)
            .subscribe()
        )
        
        print("✅ Trades listener connected!\n")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        print("🛑 Trades listener cancelled")
        if 'response' in locals():
            await response.unsubscribe()
        raise
    except Exception as e:
        print(f"❌ Error in trades listener: {e}")
        raise


async def run_all_listeners():
    """
    Runs all listeners in parallel
    """
    print("=" * 100)
    print("🚀 STARTING POLYMARKET MONITORING SYSTEM")
    print("=" * 100)
    print(f"⏰ Start time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    try:
        # Run all listeners simultaneously
        await asyncio.gather(
            listen_to_trades(),
            listen_to_positions(),
            listen_to_updates()
        )
    except KeyboardInterrupt:
        print("\n" + "=" * 100)
        print("🛑 Interrupted by user (Ctrl+C)")
        print("=" * 100)
    except Exception as e:
        print("\n" + "=" * 100)
        print(f"❌ Fatal error: {e}")
        print("=" * 100)
        raise
    finally:
        print(f"⏰ End time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("👋 System shutdown!")


def _start_polling_threads():
    """Start 5s polling threads for history and positions."""
    user_addr = config.TRADER_WALLET
    print("starting polling threads")
    if not user_addr:
        print("No user address configured for polling; skipping background polling.")
        return

    def poll_history_loop():
        while True:
            try:
                activities = fetch_history_activities(user_addr, limit=500, offset=0)
                if activities:
                    insert_history_batch(activities)
            except Exception:
                traceback.print_exc()
            time.sleep(5)

    def poll_positions_loop():
        while True:
            try:
                positions = fetch_player_positions(user_address=user_addr, limit=50, offset=0)
                if positions:
                    insert_player_positions_batch(positions)
            except Exception:
                traceback.print_exc()
            time.sleep(6 * 60)

    threading.Thread(target=poll_history_loop, daemon=True).start()
    threading.Thread(target=poll_positions_loop, daemon=True).start()


if __name__ == "__main__":
    # Print configuration summary
    config.print_config_summary()
    
    try:
        _start_polling_threads()
    except Exception:
        traceback.print_exc()

    # Run all listeners
    asyncio.run(run_all_listeners())
    
    # To run only a specific listener, comment the line above and uncomment one of the lines below:
    # asyncio.run(listen_to_trades())
    # asyncio.run(listen_to_positions())
    # asyncio.run(listen_to_updates())
    
