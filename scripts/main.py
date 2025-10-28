import os
import asyncio
from dotenv import load_dotenv
from supabase import acreate_client, AsyncClient
from make_orders import make_order
import get_ok
from constraints.sizing import sizing_constraints
from constraints.validators import has_already_an_open_position

load_dotenv()

# Config Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
async def create_supabase():
  supabase: AsyncClient = await acreate_client(url, key)
  return supabase
TABLE_NAME = "historic_trades"


def handle_new_trade(payload):
    
    transaction_hash = payload.get('data').get('record').get('transaction_hash')
    usdc_size = payload.get('data').get('record').get('usdc_size')
    side = payload.get('data').get('record').get('side')
    token_id = payload.get('data').get('record').get('asset')
    title = payload.get('data').get('record').get('title')
    
    print("\n" + "=" * 100)
    print("🔍 Nova trade recebida!")
    print('Title:', title)
    print('Asset:', transaction_hash)
    print('USDC Size:', usdc_size)
    print('Side:', side)
    print('Token ID:', token_id)

    sized_price = sizing_constraints(usdc_size)

    response = make_order(price=sized_price, size=sized_price, side=side, token_id=token_id)
    print('Response:', response)
    return response



async def listen_to_trades():
    """
    Inicia o listener para novas trades
    """
    print("🔍 Iniciando listener de trades...")
    print(f"📊 Monitorando tabela: {TABLE_NAME}")
    print()
    
    # Criar cliente ASSÍNCRONO
    supabase: AsyncClient = await acreate_client(url, key)

    response = (
    await supabase.channel("schema-db-changes")
    .on_postgres_changes("INSERT", schema="public", table=TABLE_NAME, callback=handle_new_trade)
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
    
