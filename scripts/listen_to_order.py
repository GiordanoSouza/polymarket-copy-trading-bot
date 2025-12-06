# import os
# import asyncio
# from dotenv import load_dotenv
# from supabase import acreate_client, AsyncClient

# load_dotenv()

# # Config Supabase
# url: str = os.environ.get("SUPABASE_URL")
# key: str = os.environ.get("SUPABASE_KEY")

# async def create_supabase():
#   supabase: AsyncClient = await acreate_client(url, key)
#   return supabase

# TABLE_NAME = "historic_trades"


# def handle_new_trade(payload):
    
#     transaction_hash = payload.get('data').get('record').get('transaction_hash')
#     usdc_size = payload.get('data').get('record').get('usdc_size')
#     print('transaction_hash:', transaction_hash)
#     print('usdc_size:', usdc_size)
#     return transaction_hash, usdc_size


# async def listen_to_trades():
#     """
#     Starts listener for new trades
#     """
#     print("🔍 Starting trades listener...")
#     print(f"📊 Monitoring table: {TABLE_NAME}")
#     print()
    
#     # Create ASYNC client
#     supabase: AsyncClient = await acreate_client(url, key)

#     response = (
#     await supabase.channel("schema-db-changes")
#     .on_postgres_changes("INSERT", schema="public", table=TABLE_NAME, callback=handle_new_trade)
#     .subscribe()
#     )
    
#     print("✅ Connected! Waiting for new trades...")
#     print("   (Press Ctrl+C to stop)\n")
    
#     # Keep the script running
#     try:
#         while True:
#             await asyncio.sleep(1)
#     except KeyboardInterrupt:
#         await response.unsubscribe()
#         print("✅ Successfully disconnected!")
    
    
# if __name__ == "__main__":
#     # Run the async listener
#     asyncio.run(listen_to_trades())
