# Código para obter as posições do player e detectar se alguma posição excede o limite definido
import requests
import os
from pprint import pprint
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

load_dotenv()

# config supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
proxy_wallet_self = os.environ.get("PROXY_WALLET_SELF")

API_URL = 'https://data-api.polymarket.com/positions'
MAX_LIMIT = 500  # Limite máximo da API
TABLE_NAME = "polymarket_positions"

def fetch_player_positions(user_address: str, limit: int = 500, offset: int = 0, condition_id: str = None):
    try:
        params = {
            "user": user_address,
            "limit": str(limit),
            "offset": str(offset),
            "sortBy": "INITIAL",
            "sortDirection": "DESC",
            "conditionId": condition_id,
        }
        
        response = requests.get(API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        print('data', data)
        print('data length', len(data))
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição (offset {offset}): {e}")
        return None



def transform_position_to_db_format(position: dict) -> dict:
    """
    Transforma o formato da API para o formato do banco de dados
    
    Args:
        position: Dicionário com dados da API
    
    Returns:
        Dicionário formatado para inserção no banco
    """
    # Tratar end_date: converter string vazia ou None em NULL
    end_date = position.get('endDate')
    if not end_date or end_date == '':
        end_date = None
    
    # Tratar eventId: converter string para int, ou None se vazio
    event_id = position.get('eventId')
    if event_id:
        try:
            event_id = int(event_id)
        except (ValueError, TypeError):
            event_id = None
    else:
        event_id = None
    
    return {
       'proxy_wallet': position.get('proxyWallet'),
       'asset': position.get('asset'),
       'condition_id': position.get('conditionId'),
       'size': position.get('size'),
       'avg_price': position.get('avgPrice'),
       'initial_value': position.get('initialValue'),
       'current_value': position.get('currentValue'),
       'cash_pnl': position.get('cashPnl'),
       'percent_pnl': position.get('percentPnl'),
       'total_bought': position.get('totalBought'),
       'realized_pnl': position.get('realizedPnl'),
       'percent_realized_pnl': position.get('percentRealizedPnl'),
       'cur_price': position.get('curPrice'),
       'redeemable': position.get('redeemable'),
       'mergeable': position.get('mergeable'),
       'title': position.get('title'),
       'slug': position.get('slug'),
       'icon': position.get('icon'),
       'event_id': event_id,
       'event_slug': position.get('eventSlug'),
       'outcome': position.get('outcome'),
       'outcome_index': position.get('outcomeIndex'),
       'opposite_outcome': position.get('oppositeOutcome'),
       'opposite_asset': position.get('oppositeAsset'),
       'end_date': end_date,
       'negative_risk': position.get('negativeRisk'),
    }

def insert_player_positions_batch(positions: list):
    if not positions:
        print("No positions to insert")
        return 0

    success_count = 0
    error_count = 0
    
    for idx, position in enumerate(positions, 1):
        try:
            # Transformar para formato do banco antes de inserir
            db_position = transform_position_to_db_format(position)
            supabase.table(TABLE_NAME).upsert(
                db_position,
            ).execute()
            success_count += 1
        except Exception as e:
            error_count += 1
            print(f"❌ Erro na posição {idx}/{len(positions)}: {e}")
            print(f"   Título: {position.get('title', 'N/A')}")
            print(f"   Asset: {position.get('asset', 'N/A')[:20]}...")
            print(f"   end_date recebido: '{position.get('endDate')}'")
            # Continuar processando as próximas posições
    
    print(f"\n✅ Resumo: {success_count} inseridas com sucesso, {error_count} com erro")
    return success_count




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
    positions = fetch_player_positions(user_address=proxy_wallet_self)
    # success_count = insert_player_positions_batch(positions)
    # print(f"Success count: {success_count}")
    print(positions[0])