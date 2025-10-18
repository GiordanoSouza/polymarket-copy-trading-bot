import requests
from datetime import datetime
import json

url = "https://api.domeapi.io/v1/polymarket/orders"

resp = requests.get(url, params={
    "user":"0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
    "limit":"50",
    "sortBy":"TIMESTAMP",
    "sortDirection":"DESC",
})

data = resp.json()

print("=" * 100)
print(f"ORDENS ENCONTRADAS: {len(data.get('orders', []))}")
print("=" * 100)

for i, order in enumerate(data.get('orders', []), 1):
    print(f"\n📊 ORDEM #{i}")
    print("-" * 100)
    
    # Informações principais
    print(f"Mercado: {order.get('title', 'N/A')}")
    print(f"Slug: {order.get('market_slug', 'N/A')}")
    
    # Detalhes da ordem
    print(f"\nTipo: {order.get('side', 'N/A')}")
    print(f"Preço: ${order.get('price', 0):.2f}")
    print(f"Shares: {order.get('shares_normalized', 0):.2f}")
    print(f"Shares (raw): {order.get('shares', 0):,}")
    
    # Informações de usuário e blockchain
    print(f"\nUsuário: {order.get('user', 'N/A')}")
    print(f"Transaction Hash: {order.get('tx_hash', 'N/A')}")
    print(f"Order Hash: {order.get('order_hash', 'N/A')}")
    
    # Token e condição
    print(f"\nToken ID: {order.get('token_id', 'N/A')}")
    print(f"Condition ID: {order.get('condition_id', 'N/A')}")
    
    # Timestamp
    timestamp = order.get('timestamp')
    if timestamp:
        dt = datetime.fromtimestamp(timestamp)
        print(f"\nData/Hora: {dt.strftime('%d/%m/%Y %H:%M:%S')}")
    
    print("-" * 100)

print(f"\n\n{'=' * 100}")
print("RESUMO")
print("=" * 100)

# Estatísticas resumidas
if data.get('orders'):
    total_orders = len(data['orders'])
    buy_orders = sum(1 for o in data['orders'] if o.get('side') == 'BUY')
    sell_orders = sum(1 for o in data['orders'] if o.get('side') == 'SELL')
    total_volume = sum(o.get('shares_normalized', 0) for o in data['orders'])
    
    print(f"Total de Ordens: {total_orders}")
    print(f"Ordens de Compra (BUY): {buy_orders}")
    print(f"Ordens de Venda (SELL): {sell_orders}")
    print(f"Volume Total (shares): {total_volume:.2f}")
    print("=" * 100)