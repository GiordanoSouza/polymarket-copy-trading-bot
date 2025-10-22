import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
load_dotenv()
# config supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# config api


def handle_new_trade(payload):
    print(payload)

channel = supabase.channel('historic_trades')
channel.on_postgres_changes(
    event='*',
    schema='public',
    table='historic_trades',
    callback=handle_new_trade
).subscribe()

print("Listening to orders...")