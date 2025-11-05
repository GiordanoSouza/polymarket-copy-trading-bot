import os
import asyncio
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
async def create_supabase():
  supabase: AsyncClient = await acreate_client(url, key)
  return supabase
TABLE_NAME_TRADES = "historic_trades"
TABLE_NAME_POSITIONS = "polymarket_positions"


def handle_new_trade(payload):
    
    transaction_hash = payload.get('data').get('record').get('transaction_hash')
    usdc_size = payload.get('data').get('record').get('usdc_size')
    side = payload.get('data').get('record').get('side')
    token_id = payload.get('data').get('record').get('asset')
    title = payload.get('data').get('record').get('title')
    price = payload.get('data').get('record').get('price')
    size = payload.get('data').get('record').get('size')
    
    print("\n" + "=" * 100)
    print("🔍 Nova trade recebida!")
    print('Title:', title)
    print('Asset:', transaction_hash)
    print('USDC Size:', usdc_size)
    print('Side:', side)
    print('Token ID:', token_id)

    sized_price = sizing_constraints(usdc_size)
    
    if sized_price >= 1:
        response = make_order(price=price, size=sizing_constraints(size), side=side, token_id=token_id)
        print('Response:', response)
        return response 
    else:
        print('Sized price is less than 1, skipping order')
        return None


def handle_new_position(payload):
    print('New position received')

    asset = payload.get('data').get('record').get('asset')
    initial_value = payload.get('data').get('record').get('initial_value')
    size = payload.get('data').get('record').get('size')

    print('Nova Posição recebida!')
    print('Asset:', asset)
    print('Initial value:', initial_value)
    print('Size:', size)

    if sizing_constraints(initial_value) > 1:
        print('Size is greater than 1000, making order')
        response = make_order(price=initial_value, size=sizing_constraints(size), side=BUY, token_id=asset)
        print('Response:', response)
        return response 
    else:
        print('Size is less than 1000, skipping position')
        return None

async def listen_to_positions():
    """
    Inicia o listener para novas posições
    """
    print("🔍 Iniciando listener de posições...")
    print(f"📊 Monitorando tabela: {TABLE_NAME_POSITIONS}")
    print()
    
    # Criar cliente ASSÍNCRONO
    supabase: AsyncClient = await acreate_client(url, key)

    response = (
    await supabase.channel("schema-db-changes")
    .on_postgres_changes("INSERT", schema="public", table=TABLE_NAME_POSITIONS, callback=handle_new_position)
    .subscribe()
    )
    

    print("✅ Conectado! Aguardando novas posições...")
    print("   (Pressione Ctrl+C para parar)\n")
    
    # Manter o script rodando
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await response.unsubscribe()
        print("✅ Desconectado com sucesso!")

async def listen_to_trades():
    """
    Inicia o listener para novas trades
    """
    print("🔍 Iniciando listener de trades...")
    print(f"📊 Monitorando tabela: {TABLE_NAME_TRADES}")
    print()
    
    # Criar cliente ASSÍNCRONO
    supabase: AsyncClient = await acreate_client(url, key)

    response = (
    await supabase.channel("schema-db-changes")
    .on_postgres_changes("INSERT", schema="public", table=TABLE_NAME_TRADES, callback=handle_new_trade)
    .subscribe()
    )
    

    print("✅ Conectado! Aguardando novas trades...")
    print("   (Pressione Ctrl+C para parar)\n")
    
    # Manter o script rodando
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await response.unsubscribe()
        print("✅ Desconectado com sucesso!")

if __name__ == "__main__":
    asyncio.run(listen_to_trades())
    
