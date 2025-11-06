import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from supabase import acreate_client, AsyncClient
from make_orders import make_order
import get_ok
from constraints.sizing import sizing_constraints
from constraints.validators import has_already_an_open_position
from py_clob_client.order_builder.constants import BUY, SELL

load_dotenv()

# Config Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
TABLE_NAME_TRADES = "historic_trades"
TABLE_NAME_POSITIONS = "polymarket_positions"

# Cliente Supabase compartilhado
_supabase_client: AsyncClient = None

async def get_supabase() -> AsyncClient:
    """
    Retorna uma instância singleton do cliente Supabase
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = await acreate_client(url, key)
    return _supabase_client


def handle_new_trade(payload):
    """
    Handler para novas trades inseridas
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
        
        print("\n" + "=" * 100)
        print(f"🔍 Nova trade recebida! [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"📝 Title: {title}")
        print(f"🔑 Transaction Hash: {transaction_hash}")
        print(f"💰 USDC Size: {usdc_size}")
        print(f"📊 Side: {side}")
        print(f"🎯 Token ID: {token_id}")
        print(f"💵 Price: {price}")
        print("=" * 100)

        sized_price = sizing_constraints(usdc_size)

        if side == SELL:
            print(f"⏭️  Side is SELL, checking the % of the position from the TRADER")
            
        
        if sized_price >= 1:
            print(f"✅ Sized price ({sized_price}) >= 1, fazendo ordem...")
            response = make_order(price=price, size=sizing_constraints(size), side=side, token_id=token_id)
            print(f"📤 Response: {response}")
            return response 
        else:
            print(f"⏭️  Sized price ({sized_price}) < 1, pulando ordem")
            return None
    except Exception as e:
        print(f"❌ Erro ao processar nova trade: {e}")
        return None


def handle_new_position(payload):
    """
    Handler para novas posições inseridas
    """
    try:
        record = payload.get('data', {}).get('record', {})
        
        # Campos do Polymarket (camelCase)
        asset = record.get('asset')
        initial_value = record.get('initialValue')  # ✅ Corrigido: camelCase
        size = record.get('size')
        avg_price = record.get('avgPrice', 0)
        title = record.get('title', 'N/A')
        outcome = record.get('outcome', 'N/A')
        proxy_wallet = record.get('proxyWallet', 'N/A')

        print("\n" + "=" * 100)
        print(f"📈 Nova posição recebida! [{datetime.now().strftime('%H:%M:%S')}]")
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
            print(f"✅ Sized value ({sized_value}) > 1, fazendo ordem de compra...")
            response = make_order(price=avg_price, size=sizing_constraints(size), side=BUY, token_id=asset)
            print(f"📤 Response: {response}")
            return response 
        else:
            print(f"⏭️  Sized value ({sized_value}) <= 1, pulando posição")
            return None
    except Exception as e:
        print(f"❌ Erro ao processar nova posição: {e}")
        import traceback
        traceback.print_exc()
        return None


def handle_update_position(payload):
    """
    Handler para atualizações de posições existentes
    """
    try:
        old_record = payload.get('data', {}).get('old_record', {})
        new_record = payload.get('data', {}).get('record', {})
        
        # Campos do Polymarket (camelCase)
        asset = new_record.get('asset')
        title = new_record.get('title', 'N/A')
        outcome = new_record.get('outcome', 'N/A')
        
        old_value = old_record.get('currentValue', 0)  # ✅ Corrigido: camelCase
        new_value = new_record.get('currentValue', 0)  # ✅ Corrigido: camelCase
        old_size = old_record.get('size', 0)
        new_size = new_record.get('size', 0)
        
        # Informações de PnL
        cash_pnl = new_record.get('cashPnl', 0)
        percent_pnl = new_record.get('percentPnl', 0)
        cur_price = new_record.get('curPrice', 0)
        avg_price = new_record.get('avgPrice', 0)
        
        print("\n" + "=" * 100)
        print(f"🔄 Atualização de posição recebida! [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"📝 Title: {title}")
        print(f"🎲 Outcome: {outcome}")
        print(f"🎯 Asset: {asset}")
        print(f"💰 Valor: ${old_value:.4f} → ${new_value:.4f} (Δ: ${new_value - old_value:+.4f})")
        print(f"📊 Size: {old_size} → {new_size} (Δ: {new_size - old_size:+.2f})")
        print(f"💵 Preço: Avg ${avg_price:.4f} | Atual ${cur_price:.4f}")
        print(f"📈 PnL: ${cash_pnl:+.4f} ({percent_pnl:+.1f}%)")
        print("=" * 100)
        
        # Aqui você pode adicionar lógica específica para atualizações
        # Exemplo: Take profit se PnL% > 50%, Stop loss se < -20%, etc.
        if percent_pnl >= 50:
            print(f"🎉 PnL positivo de {percent_pnl}%! Considere realizar lucros.")
        elif percent_pnl <= -20:
            print(f"⚠️  PnL negativo de {percent_pnl}%! Considere stop loss.")
        
        return None
    except Exception as e:
        print(f"❌ Erro ao processar atualização de posição: {e}")
        import traceback
        traceback.print_exc()
        return None

async def listen_to_positions():
    """
    Inicia o listener para novas posições (INSERTs)
    """
    print("🔍 Iniciando listener de posições...")
    print(f"📊 Monitorando tabela: {TABLE_NAME_POSITIONS} (INSERT)")
    
    try:
        # Usar cliente compartilhado
        supabase = await get_supabase()

        response = (
            await supabase.channel("positions-inserts")
            .on_postgres_changes("INSERT", schema="public", table=TABLE_NAME_POSITIONS, callback=handle_new_position)
            .subscribe()
        )
        
        print("✅ Listener de posições conectado!\n")
        
        # Manter rodando até ser interrompido
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        print("🛑 Listener de posições cancelado")
        if 'response' in locals():
            await response.unsubscribe()
        raise
    except Exception as e:
        print(f"❌ Erro no listener de posições: {e}")
        raise

async def listen_to_updates():
    """
    Inicia o listener para atualizações de posições (UPDATEs)
    """
    print("🔍 Iniciando listener de atualizações...")
    print(f"📊 Monitorando tabela: {TABLE_NAME_POSITIONS} (UPDATE)")
    
    try:
        # Usar cliente compartilhado
        supabase = await get_supabase()
        
        response = (
            await supabase.channel("positions-updates")
            .on_postgres_changes("UPDATE", schema="public", table=TABLE_NAME_POSITIONS, callback=handle_update_position)
            .subscribe()
        )

        print("✅ Listener de atualizações conectado!\n")
        
        # Manter rodando até ser interrompido
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        print("🛑 Listener de atualizações cancelado")
        if 'response' in locals():
            await response.unsubscribe()
        raise
    except Exception as e:
        print(f"❌ Erro no listener de atualizações: {e}")
        raise

async def listen_to_trades():
    """
    Inicia o listener para novas trades (INSERTs)
    """
    print("🔍 Iniciando listener de trades...")
    print(f"📊 Monitorando tabela: {TABLE_NAME_TRADES} (INSERT)")
    
    try:
        # Usar cliente compartilhado
        supabase = await get_supabase()

        response = (
            await supabase.channel("trades-inserts")
            .on_postgres_changes("INSERT", schema="public", table=TABLE_NAME_TRADES, callback=handle_new_trade)
            .subscribe()
        )
        
        print("✅ Listener de trades conectado!\n")
        
        # Manter rodando até ser interrompido
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        print("🛑 Listener de trades cancelado")
        if 'response' in locals():
            await response.unsubscribe()
        raise
    except Exception as e:
        print(f"❌ Erro no listener de trades: {e}")
        raise


async def run_all_listeners():
    """
    Executa todos os listeners em paralelo
    """
    print("=" * 100)
    print("🚀 INICIANDO SISTEMA DE MONITORAMENTO POLYMARKET")
    print("=" * 100)
    print(f"⏰ Hora de início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    try:
        # Executar todos os listeners simultaneamente
        await asyncio.gather(
            listen_to_trades(),
            listen_to_positions(),
            listen_to_updates()
        )
    except KeyboardInterrupt:
        print("\n" + "=" * 100)
        print("🛑 Interrompido pelo usuário (Ctrl+C)")
        print("=" * 100)
    except Exception as e:
        print("\n" + "=" * 100)
        print(f"❌ Erro fatal: {e}")
        print("=" * 100)
        raise
    finally:
        print(f"⏰ Hora de término: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("👋 Sistema encerrado!")


if __name__ == "__main__":
    # Executar todos os listeners
    asyncio.run(run_all_listeners())
    
    # Para rodar apenas um listener específico, comente a linha acima e descomente uma das linhas abaixo:
    # asyncio.run(listen_to_trades())
    # asyncio.run(listen_to_positions())
    # asyncio.run(listen_to_updates())
    
