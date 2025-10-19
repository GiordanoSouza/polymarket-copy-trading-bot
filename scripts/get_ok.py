from py_clob_client.client import ClobClient
import time
from datetime import datetime

client = ClobClient("https://clob.polymarket.com")  # Level 0 (no auth)

ok = client.get_ok()
time = client.get_server_time()

print(ok, time)
print("Time:", datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S"))