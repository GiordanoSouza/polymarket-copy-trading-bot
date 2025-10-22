import os
import asyncio
from dotenv import load_dotenv
from supabase import acreate_client, AsyncClient

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
    print('transaction_hash:', transaction_hash)


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
    # Executar o listener assíncrono
    asyncio.run(listen_to_trades())