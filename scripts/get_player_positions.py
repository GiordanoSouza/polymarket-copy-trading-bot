# Código para obter as posições do player e detectar se alguma posição excede o limite definido
import requests
import os
from pprint import pprint

URL = 'https://data-api.polymarket.com/positions'

def get_player_positions(user_address: str):
    response = requests.get(URL, params={'user': user_address})
    return response.json()

def print_positions_readable(positions: list):
    if not positions:
        print("\n⚠️  Nenhuma posição encontrada para esse usuário.\n")
        return
    print("\n📊 Posições do jogador:\n" + "="*80)
    for idx, pos in enumerate(positions, 1):
        print(f"🔹 Posição #{idx}:")
        print(f"   🏷️  Mercado: {pos.get('title', 'N/A')} ({pos.get('slug', '-')})")
        print(f"   ➡️  Outcome: {pos.get('outcome', 'N/A')}")
        print(f"   📈 Size (tamanho): {pos.get('size', 0):,.4f}")
        print(f"   💵 Valor inicial:  {pos.get('initialValue', 0):,.2f}")
        print(f"   📊 Valor atual:    {pos.get('currentValue', 0):,.2f}")
        print(f"   ℹ️  PnL:           {pos.get('cashPnl', 0):,.2f} USDC ({pos.get('percentPnl', 0):.2f}%)")
        print(f"   🔗 Asset ID:       {pos.get('asset', 'N/A')}")
        print(f"   📅 Data de expiração: {pos.get('endDate', 'N/A')}")
        print("-"*80)
    print()

def detect_big_positions(positions: list, size_limit: float = 1000.0):
    """Retorna uma lista das posições acima do limite definido."""
    big_positions = []
    for position in positions:
        if position.get('initialValue', 0) > size_limit:
            big_positions.append(position)
    return big_positions

if __name__ == '__main__':
    user = '0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b'
    positions = get_player_positions(user)
    print_positions_readable(positions)
    big_positions = detect_big_positions(positions, size_limit=5000.0)
    if big_positions:
        print("🚨 Posições acima do limite definido:")
        print_positions_readable(big_positions)
    else:
        print("✅ Nenhuma posição acima do limite definido.")